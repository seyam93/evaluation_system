import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import EvaluationSession
from students.models import Person as Candidate


class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.session_group_name = f'session_{self.session_id}'

        # Join session group
        await self.channel_layer.group_add(
            self.session_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave session group
        await self.channel_layer.group_discard(
            self.session_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']

        if action == 'set_candidate':
            candidate_id = text_data_json['candidate_id']
            user = self.scope['user']

            # Verify user is authenticated and is the examiner
            result = await self.set_current_candidate(candidate_id, user)

            if result['success']:
                # Send immediate confirmation to the sender first
                await self.send(text_data=json.dumps({
                    'type': 'candidate_updated',
                    'candidate_id': candidate_id,
                    'candidate_name': result['candidate_name'],
                    'updated_by': user.id,
                    'confirmed': True
                }))

                # Then broadcast to all other connected clients
                await self.channel_layer.group_send(
                    self.session_group_name,
                    {
                        'type': 'candidate_updated',
                        'candidate_id': candidate_id,
                        'candidate_name': result['candidate_name'],
                        'user_id': user.id
                    }
                )
            else:
                # Send error back to the specific client
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result['error']
                }))

    # Receive message from session group
    async def candidate_updated(self, event):
        candidate_id = event['candidate_id']
        candidate_name = event['candidate_name']
        user_id = event['user_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'candidate_updated',
            'candidate_id': candidate_id,
            'candidate_name': candidate_name,
            'updated_by': user_id
        }))

    @database_sync_to_async
    def set_current_candidate(self, candidate_id, user):
        try:
            # Use select_related to minimize database queries
            session = EvaluationSession.objects.select_related('plan', 'current_candidate').get(
                id=self.session_id,
                examiner=user
            )

            # Get the candidate and verify they belong to this session's plan
            candidate = session.plan.candidates.get(id=candidate_id)

            # Update the session's current candidate (single query)
            session.current_candidate_id = candidate_id
            session.save(update_fields=['current_candidate'])

            return {
                'success': True,
                'candidate_name': candidate.student_name
            }

        except EvaluationSession.DoesNotExist:
            return {
                'success': False,
                'error': 'Session not found or you are not the examiner'
            }
        except Candidate.DoesNotExist:
            return {
                'success': False,
                'error': 'Candidate not found in this plan'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }