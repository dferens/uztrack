$(function() {
  $.fn.bootstrapSwitch.defaults.onColor = 'success';

  $('#id_enabled').bootstrapSwitch({
    onSwitchChange: function(event, state) {
      $.ajax({
        type: 'POST',
        data: {enabled: state},
        beforeSend: function(xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
        },
      })
    }
  });
});

