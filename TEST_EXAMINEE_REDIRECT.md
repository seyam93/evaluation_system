# Testing Examinee Auto-Redirect

## How to Test:

1. **Access Login Page**: Go to `http://127.0.0.1:8000/`

2. **Login as Examinee**:
   - Username: `candidate1`
   - Password: `examinee123`

3. **Expected Result**:
   - Should automatically redirect to `http://127.0.0.1:8000/evaluation/examinee/`
   - Should see personalized welcome: "مرحباً أحمد محمد"
   - Should show user type: "Examinee/Candidate"

## Alternative Test Routes:

- **Direct Home**: `http://127.0.0.1:8000/core/home/` - Should also redirect
- **Dashboard**: `http://127.0.0.1:8000/dashboard/` - Should also redirect

## What Should Happen:

✅ **After Login**: Automatic redirect to examinee dashboard
✅ **Personalized Welcome**: Shows actual user's name
✅ **Access Control**: Only examinees can access the page
✅ **Real-time Updates**: Shows current candidate info

## Test Other User Types:

- **Committee User**: Should redirect to committee dashboard
- **Examiner User**: Should redirect to examiner dashboard
- **Admin User**: Should redirect to admin dashboard

## Expected Behavior:

All user types now have automatic redirects based on their role, providing a seamless user experience.