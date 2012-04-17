(function($){
    var     globalInitialized = false;
    var     menuItem = null;

    var getMenu = function(e) {
        return e.find('.options');
    }

    var dropDownMenuOpen = function(e, options) {
        if (e != menuItem)
            dropDownMenuClose(menuItem, options);
        var o = getMenu(e);
        o.css({visibility: "visible", display: 'none'})
        o.stop().slideDown(options.speed, function() { e.addClass('active'); })
        menuItem = e;
    };

    var dropDownMenuClose = function(e, options) {
        if (e == null) 
            return;
        var o = getMenu(e);
        o.css({visibility: "none", display: 'auto'})
        o.stop().slideUp(options.speed, function() { e.removeClass('active'); })
        menuItem = null;
    };

    $.fn.extend({
        dropDownMenu: function(options) {
            var defaults = {
                speed: 200,
            };

            var options =  $.extend(defaults, options);

            if (!globalInitialized) {
                $(document).bind('click', function(evt) {
                    if (menuItem) {
                        var clicked = $(evt.target);

                        if (! clicked.parents().data("DROP_DOWN_MENU"))
                            dropDownMenuClose(menuItem, options)
                    }
                });
                globalInitiailzed = true;
            }

            var clickHandler = function(evt) {
                var e = $(evt.currentTarget);

                if (e.hasClass('active')) {
                    dropDownMenuClose(e, options)
                } else {
                    dropDownMenuOpen(e, options)
                }
            };

            return this.each(function() {
                $(this).bind('click', clickHandler);
                $(this).data("DROP_DOWN_MENU", 1);
            });
        }
    });
})(jQuery);

(function($) {
    var defaults = {
        use_fade   : false,
        closeImage : "/static/image/close.png"
    };

    $.fn.extend({
        MessageBar : function(message, opts) {
            var $this = $(this);
            var options = $.extend(defaults, opts || {});
            var messageDiv = $this.children('.messageBar');
            
            if (messageDiv.size() == 0) {
                messageDiv = $('<div class="messageBar"></div>');
                $this.prepend(messageDiv);
            }

            allDone = function() {
                if (messageDiv && messageDiv.childElementCount == 0) {
                    messageDiv.remove();
                    messageDiv = null;
                }
            };

            var closeHtml;

            if (options.closeImage) {
                closeHtml = '<img src="' + options.closeImage + '"/>';
            } else {
                closeHtml = '<a href="#">[X]</a>';
            }
            var msg = $('<div class="message">' + message + '<div class="dismiss">' + closeHtml + '</div></div>');

            if (options.type) 
                msg.addClass(options.type);
            msg.hide();

            messageDiv.append(msg);

            var timer = null;
            if (options.timeout)
                timer = setTimeout(function() { $('.dismiss', msg).click() }, options.timeout * 1000);

            if (options.use_fade) 
                msg.fadeIn(allDone);
            else
                msg.slideDown(allDone);

            $('.dismiss', msg).click(function(evt) {
                if (timer)
                    clearTimeout(timer);
                    
                if (options.use_fade) 
                    msg.fadeOut(allDone);
                else
                    msg.slideUp(allDone);
                evt.stopPropagation();
            });
        }
    });
})(jQuery);

$(document).ready(function() {
    $('.drop-down-menu').dropDownMenu();
});
