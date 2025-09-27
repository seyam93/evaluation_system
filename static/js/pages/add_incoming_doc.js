document.addEventListener("DOMContentLoaded", function () {
  $(".select2").select2({});
});



$("#save_incoming_doc").click(function () {
  Swal.fire({
    title: "حفظ وإرسال المكاتبة",
    text: "هل تريد حفظ المكاتبة وإرسالها للمستوى الأعلى",
    icon: "warning",
    showCancelButton: !0,
    confirmButtonColor: "#34c38f",
    cancelButtonColor: "#f46a6a",
    confirmButtonText: "حفظ",
    cancelButtonText: "إلغاء",
  }).then(function (t) {
    if ($("#incoming_doc_form").valid()) {
      var selectedRadioValue = $("input[name='main_unit']:checked").closest("tr").attr("id");
      var selectedCheckboxValues = [];
      $("input[name='sub_unit']:checked").each(function () {
        selectedCheckboxValues.push($(this).closest("tr").attr("id"));
      });
      if (t.value) {
        if (selectedRadioValue == null) {
          Swal.fire(
            "خطأ",
            "يجب أختيار فرع / اتجاه اساسي",
            "error"
          );
        }else{
          $("#incoming_doc_form").submit();
          Swal.fire(
            "تم الحفظ",
            "تم حفظ المكاتبة وإرسالها للمستوى الأعلى",
            "success"
          );

        }

      }
    } else {
      $("#incoming_doc_form").addClass("was-validated");
    }
  });
});
$("#save-assignment").on("click", function () {
  $("#addAssignmentForm").submit();
});
var unitsAssignments = []
$('#addAssignmentForm').submit(function(e){
  e.preventDefault();
  var formDataObject = {};
  var formData = new FormData(this);
  formData.forEach(function(value, key){
    formDataObject[key] = value;
  });
  var existingIndex = unitsAssignments.findIndex(function (item) {
    return item.unit_id === formDataObject.unit_id;
  });

  if (existingIndex !== -1) {
    unitsAssignments[existingIndex] = formDataObject;
  } else {
    unitsAssignments.push(formDataObject);
  }

  this.reset();
  toastr["success"]("تم إضافة التكليف", "عملية ناجحة");
  $('.add_assignment_modal').modal('hide');
});
$(document).ready(function () {
  $('.assignment-button').click(function () {
      var unitId = $(this).closest('tr').attr('id');
      $('#unitIdInput').val(unitId);
  });
});

$("#incoming_doc_form").submit(function (e) {
  e.preventDefault();
  var formData = new FormData(this);
  var selectedRadioValue = $("input[name='main_unit']:checked").closest("tr").attr("id");
  var selectedCheckboxValues = [];
  $("input[type='checkbox']:checked").each(function () {
    selectedCheckboxValues.push($(this).closest("tr").attr("id"));
  });

  formData.append("main_unit", selectedRadioValue);
  formData.append("sub_units", selectedCheckboxValues);
  formData.append("unitsAssignments", JSON.stringify(unitsAssignments));
  $.ajax({
    method: "POST",
    url: window.location.href,
    data: formData,
    contentType: false,
    processData: false,
    success: function (data) {
      toastr["success"]("تم إضافة مكتب المصدر بنجاح", "عملية ناجحة");
      window.location.href = data.redirect_url;
    },
    error: function (error_data) {
      toastr["error"](error_data.responseText, "خطأ!");
    },
  });
});

function delete_item(id) {
  Swal.fire({
    title: "هل انت متاكد؟",
    text: "هل تريد حذف هذا المسلسل" + " ('" + id + "')",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#dc3545",
    confirmButtonText: "نعم, احذف",
    cancelButtonText: "لا تحذف",
  }).then((result) => {
    if (result.isConfirmed) {
      $.ajax({
        method: 'POST',
        url: window.location.href,
        data: {
          id: id,
          csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
          type: 'delete'
        },
        success: function (data) {
          $('#' + id).remove();
          Swal.fire({
            title: "تم الحذف!",
            text: "تم حذف المسلسل",
            icon: "success",
            confirmButtonText: "حسناً",
          });
        }
      });
    }
  });
}
