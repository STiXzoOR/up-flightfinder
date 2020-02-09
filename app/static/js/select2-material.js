(function(document, $, undefined) {
  $.fn.hasAttr = function(attr) {
    var attr = $(this).attr(attr);
    return typeof attr !== typeof undefined && attr !== false;
  };

  $.fn.sm_select = function(options) {
    var defaults = $.extend(
      {
        input_text: "Select option...",
        duration: 200
      },
      options
    );
    return this.each(function(e) {
      $(this).select2(options);

      var $select = $(this);
      var $select2 = $(this).data("select2");

      var $container = $select2.$container;
      var $selection = $select2.$selection;
      var $dropdownObj = $select2.dropdown;
      var $results = $select2.$results;
      var $floatingLabel = $select.closest(".floating-label");
      var multiple = $select.hasAttr("multiple");
      var selectState;

      if (multiple) {
        var first = $select.children().first();
        if (first.text() == "") {
          first.remove();
        }
      }

      $select.on("select2:focus", function(e) {
        $floatingLabel.addClass("is-focused has-value");
      });

      $select.on("select2:blur", function(e) {
        $floatingLabel.removeClass("is-focused");
      });

      $select.on("select2:open", function(e) {
        if (!multiple) {
          $dropdownObj.$search.attr(
            "placeholder",
            $(this).attr("placeholder") != undefined
              ? $(this).attr("placeholder")
              : defaults.input_text
          );
        }
        $dropdownObj.$dropdown.hide();
        setTimeout(function() {
          $dropdownObj.$dropdown
            .css("opacity", 0)
            .stop(true, true)
            .slideDown(defaults.duration, "swing", function() {
              if (!multiple) {
                $dropdownObj.$search.focus();
              }
            })
            .animate(
              { opacity: 1 },
              { queue: false, duration: defaults.duration }
            );
        }, 10);

        selectState = true;
      });
      // $select.on("select2:closing", function(e) {
      //   if (selectState) {
      //     e.preventDefault();
      //     drop_down = $("body > .select2-container .select2-dropdown");
      //     drop_down
      //       .slideUp(defaults.duration, "swing", function() {
      //         $select.select2("close");
      //       })
      //       .animate(
      //         { opacity: 0 },
      //         {
      //           queue: false,
      //           duration: defaults.duration,
      //           easing: "swing"
      //         }
      //       );
      //     selectState = false;
      //   }
      // });
      $select.on("select2:close", function(e) {
        var selectedValue = $(this).val();
        if (
          selectedValue == 0 ||
          selectedValue == "" ||
          selectedValue == undefined
        ) {
          $floatingLabel.removeClass("has-value");
        } else {
          $floatingLabel.addClass("has-value");
        }
      });

      if (multiple) {
        $select.on("change", function(e) {
          var items = $selection.children().children();
          if (!items.hasClass("select2-selection__choice")) {
            $floatingLabel.removeClass("has-value");
          } else {
            $floatingLabel.addClass("has-value");
          }
        });
      }
    });
  };
})(document, jQuery);
