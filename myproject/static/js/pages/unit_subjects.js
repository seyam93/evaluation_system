


$('#add_subject').submit(function (e) {
    e.preventDefault();
    if ($('#add_subject').valid()) {
        $.ajax({
            method: 'POST',
            url: window.location.href,
            data: new FormData(this),
            contentType: false,
            processData: false,
            success: function (data) {
                toastr["success"]("تم إضافة الموضوع بنجاح", "عملية ناجحة");
                $('.add_subject_modal').modal('hide');
                $('#add_subject').trigger("reset");
                $('#add_subject').attr('class', 'needs-validation');
                add_list_row(data);
            },
            error: function (error_data) {
                toastr["error"](error_data.responseText, "خطأ!");
            }
        });
    }
});



function add_list_row(data) {
    $('#subjects_list').append(`
    <tr id="`+ data.subject_id +`">
        <td>
        `+ data.subject_id +`
        </td>
        <td>
        `+ data.subject_name +`
        </td>
        <td>
            `+ data.subject_num +`
        </td>
        <td>
            <ul class="list-inline mb-0">
                <li class="list-inline-item">
                    <a class="text-primary"
                        href="javascript:edit_def_cat_popup(`+ data.subject_id +`)">
                        <i class="uil uil-pen font-size-18">
                        </i>
                    </a>
                </li>
                <li class="list-inline-item">

                    <a class="text-danger" href="javascript:delete_item(`+ data.subject_id +`)">
                        <i class="uil uil-trash-alt font-size-18">
                        </i>
                    </a>
                </li>
            </ul>
        </td>
    </tr>
    `);
}


function edit_subject_popup(code) {
    $.ajax({
        method: 'GET',
        url: window.location.href,
        data: {
            'code': code,
            'type': "get_data",
        },
        success: function (data) {
            edit_popup_data(data);
            $('.edit_subject_modal').modal("show");
        },
        error: function (error_data) {
            toastr["error"](error_data.responseText, "خطأ!");
        }
    });
}

$('#edit_subject').submit(function (e) {
    e.preventDefault();
    if ($('#edit_subject').valid()) {
        $.ajax({
            method: 'POST',
            url: window.location.href,
            data: new FormData(this),
            contentType: false,
            processData: false,
            success: function (data) {
                toastr["success"]("تم تحديث الموضوع بنجاح", "عملية ناجحة");
                $('.edit_subject_modal').modal('hide');
                $('#edit_subject').trigger("reset");
                $('#edit_subject').attr('class', 'needs-validation');
                edit_list_row(data);
            },
            error: function (error_data) {
                toastr["error"](error_data.responseText, "خطأ!");
            }
        });
    }
});

function edit_popup_data(data) {
    $('input[name=edit_subject_name]').val(data.subject_name);
    $('input[name=edit_subject_id]').val(data.subject_id);
    $('input[name=edit_subject_num]').val(data.subject_num);
}

function edit_list_row(data) {
    $('#' + data.subject_id).html(`
        <td>
        `+ data.subject_id +`
        </td>
        <td>
        `+ data.subject_name +`
        </td>
        <td>
            `+ data.subject_num +`
        </td>
        <td>
            <ul class="list-inline mb-0">
                <li class="list-inline-item">
                    <a class="text-primary"
                        href="javascript:edit_def_cat_popup(`+ data.subject_id +`)">
                        <i class="uil uil-pen font-size-18">
                        </i>
                    </a>
                </li>
                <li class="list-inline-item">
                    <a class="text-danger" href="javascript:delete_item(`+ data.subject_id +`)">
                        <i class="uil uil-trash-alt font-size-18">
                        </i>
                    </a>
                </li>
            </ul>
        </td>
    `);
}
