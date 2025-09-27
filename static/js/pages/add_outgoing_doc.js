document.addEventListener("DOMContentLoaded", function () {
    $(".select2").select2({});
  });
  $("#save_outgoing_doc").click(function () {
    Swal.fire({
      title: "حفظ وإرسال المكاتبة",
      text: "هل تريد حفظ المكاتبة وإرسالها للمستوى الأعلى للتصديق",
      icon: "warning",
      showCancelButton: !0,
      confirmButtonColor: "#34c38f",
      cancelButtonColor: "#f46a6a",
      confirmButtonText: "حفظ",
      cancelButtonText: "إلغاء",
    }).then(function (t) {
      if ($("#outgoing_doc_form").valid()) {
        var selectedRadioValue = $("input[name='main_unit']:checked").closest("tr").attr("id");
        var selectedCheckboxValues = [];
        $("input[name='sub_unit']:checked").each(function () {
          selectedCheckboxValues.push($(this).closest("tr").attr("id"));
        });
        if (t.value) {
          if (selectedRadioValue == null) {
            console.log("error")
            Swal.fire(
              "خطأ",
              "يجب أختيار فرع / اتجاه اساسي",
              "error"
            );
          }else{
            $("#outgoing_doc_form").submit();
            Swal.fire(
              "تم الحفظ",
              "تم حفظ المكاتبة وإرسالها للمستوى الأعلى للتصديق",
              "success"
            );
          }
  
        }
      } else {
        $("#outgoing_doc_form").addClass("was-validated");
      }
    });
  });
  
    var unitAssignments = [] 
      function saveFormData() {
        var formDataObject = {};
          formDataObject.unitId = $("#unitIdInput").val();
          formDataObject.assignmentDescription = $("textarea[name='assignment_description']").val();
          formDataObject.assignmentDeadline = $("input[name='assignment_deadline']").val();
          unitAssignments.push(formDataObject);
          console.log(unitAssignments);
      }
      $("#save-assignment").click(function () {
          saveFormData();
      });
  
  
  $("#outgoing_doc_form").submit(function (e) {
    e.preventDefault();
    var formData = new FormData(this);
    formData.append("unitAssignments", JSON.stringify(unitAssignments));
    var selectedRadioValue = $("input[name='main_unit']:checked").closest("tr").attr("id");
    var selectedCheckboxValues = [];
    $("input[type='checkbox']:checked").each(function () {
      selectedCheckboxValues.push($(this).closest("tr").attr("id"));
    });
  
    formData.append("main_unit", selectedRadioValue);
    formData.append("sub_units", selectedCheckboxValues);
    $.ajax({
      method: "POST",
      url: window.location.href,
      data: formData,
      contentType: false,
      processData: false,
      success: function (data) {
        toastr["success"]("تم حفظ المكاتبة في المسودة وارسالها للمستوى الاعلى", "عملية ناجحة");
        $(".add_def_off_modal").modal("hide");
        $("#add_def_off").trigger("reset");
        $("#add_def_off").attr("class", "needs-validation");
        $(".select2-selection--single").css("border-color", "");
        $(".searchable-combobox-modal").val("").trigger("change");
        $(".select2-selection__placeholder").html("لا يوجد");
        add_list_row(data);
      },
      error: function (error_data) {
        toastr["error"](error_data.responseText, "خطأ!");
      },
    });
  });
  
  $('#add_task_modal').submit(function(e){
    console.log("submitted")
    e.preventDefault();
    $.ajax({
        method: 'POST',
        url: window.location.href,
        data: new FormData(this),
        contentType: false,
        processData: false,
        success: function (data) {
            toastr["success"]("تم إضافة المكتب بنجاح", "عملية ناجحة");
    
        },
        error: function (error_data) {
            toastr["error"](error_data.responseText, "خطأ!");
        }
    });
  });
  
  
  $(document).ready(function () {
    $('.assignment-button').click(function () {
        var unitId = $(this).closest('tr').attr('id');
        $('#unitIdInput').val(unitId);
    });
  });