!function(){"use strict";function e(){$(".flash-message").slideDown("fast")}function s(){$(".flash-message").slideUp("fast")}$.ajaxSetup({beforeSend:function(e,s){/^(GET|HEAD|OPTIONS|TRACE)$/i.test(s.type)||e.setRequestHeader("X-CSRFToken",g.csrfToken)}}),setTimeout(e,200),setTimeout(s,2e3)}();