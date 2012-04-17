/**
*  Ajax Autocomplete for jQuery, version 1.0
*  (c) 2012 David Koblas
*
*  Ajax Autocomplete for jQuery, version 1.1.3
*  (c) 2010 Tomas Kirda
*
*  Ajax Autocomplete for jQuery is freely distributable under the terms of an MIT-style license.
*  For details, see the web site: http://www.devbridge.com/projects/autocomplete/jquery/
*
*  Last Review: 04/19/2010
*/

/*jslint onevar: true, evil: true, nomen: true, eqeqeq: true, bitwise: true, regexp: true, newcap: true, immed: true */
/*global window: true, document: true, clearInterval: true, setInterval: true, jQuery: true */

(function($) {
    var reEscape = new RegExp('(\\' + ['/', '.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '\\'].join('|\\') + ')', 'g');

    function Autocomplete(el, url, options) {
        this.el = $(el);
        this.el.attr('autocomplete', 'off');
        this.currentValue = this.el.val();

        this.badQueries = [];
        this.selectedIndex = -1;
        this.intervalId = 0;
        this.cachedResponse = [];
        this.onChangeInterval = null;
        this.ignoreValueChange = false;
        this.isLocal = false;
        this.enabled = true;

        this.url = url;

        this.options = $.extend({
                            autoSubmit: true,
                            minChars: 3,
                            useCache: true,
                            delay: 500,
                            sortResults: false,
                            filterResults: false,
                            remoteDataType: 'json',
                            remoteQueryType: 'GET',
                            params: {},
                            formatItem: this.formatItem,
                            showItem: this.showItem
                        }, options || {});

        this.initialize();
    }

    $.fn.autocomplete = function(url, options) {
        return new Autocomplete(this.get(0)||$('<input />'), url, options);
    };

    Autocomplete.prototype = {
        killerFn: null,

        initialize: function() {
            var self = this;
            var uid = Math.floor(Math.random()*0x100000).toString(16);

            this.killerFn = function(e) {
                if ($(e.target).parents('.autocomplete').size() === 0) {
                    self.killSuggestions();
                    self.disableKillerFn();
                }
            };

            this.options.width = this.options.width || this.el.width();

            var autocompleteElId = 'Autocomplete_' + uid;
            this.mainContainerId = 'AutocompleteContainter_' + uid;

            $('<div id="' + this.mainContainerId + '" style="position:absolute;z-index:9999;"><div class="autocomplete-w1"><div class="autocomplete" id="' + autocompleteElId + '" style="display:none; width:300px;"></div></div></div>').appendTo('body');

            this.container = $('#' + autocompleteElId);
            this.mainContinaer = $('#' + this.mainContainerId);

            this.fixPosition();
            this.el.bind({
                keydown  : function(e) { return self.onKeyPress(e); },
                keyup    : function(e) { return self.onKeyUp(e); },
                blur     : function(e) { return self.enableKillerFn(e); },
                focus    : function(e) { return self.fixPosition(e); }
            })
        },

        clearCache: function(){
            this.cachedResponse = [];
            this.badQueries = [];
        },
    
        disable: function(){
            this.disabled = true;
        },
    
        enable: function(){
            this.disabled = false;
        },

        fixPosition: function() {
            var offset = this.el.offset();
            this.mainContinaer.css({
                top : (offset.top + this.el.innerHeight()) + 'px', 
                left: offset.left + 'px' 
            });
        },

        enableKillerFn: function() {
            $(document).bind('click', this.killerFn);
        },

        disableKillerFn: function() {
            $(document).unbind('click', this.killerFn);
        },

        killSuggestions: function() {
            var self = this;
            this.stopKillSuggestions();
            this.intervalId = window.setInterval(function() { self.hide(); self.stopKillSuggestions(); }, 300);
        },

        stopKillSuggestions: function() {
            window.clearInterval(this.intervalId);
            this.intervalId = null;
        },

        onKeyPress: function(e) {
            if (!this.enabled || this.disabled) 
                return;

            // return will exit the function
            // and event will not be prevented
            switch (e.keyCode) {
            case 27: //KEY_ESC:
                this.el.val(this.currentValue);
                this.hide();
                break;
            case 9: //KEY_TAB:
            case 13: //KEY_RETURN:
                if (this.selectedIndex === -1) {
                    this.hide();
                    return;
                }
                this.select(this.selectedIndex, this.suggestions[this.selectedIndex]);
                if(e.keyCode === 9){ return; }
                break;
            case 38: //KEY_UP:
                this.moveUp();
                break;
            case 40: //KEY_DOWN:
                this.moveDown();
                break;
            default:
                return;
            }
            e.stopImmediatePropagation();
            e.preventDefault();
        },

        onKeyUp: function(e) {
            if(this.disabled)
                return;
            switch (e.keyCode) {
            case 38: //KEY_UP:
            case 40: //KEY_DOWN:
                return;
            }

            clearInterval(this.onChangeInterval);
            if (this.currentValue !== this.el.val()) {
                if (this.options.deferRequestBy > 0) {
                    // Defer lookup in case when value changes very quickly:
                    var self = this;
                    this.onChangeInterval = setInterval(function() { self.onValueChange(); }, this.options.deferRequestBy);
                } else {
                    this.onValueChange();
                }
            }
        },

        onValueChange: function() {
            clearInterval(this.onChangeInterval);
            this.currentValue = this.el.val();
            var q = this.getQuery(this.currentValue);
            this.selectedIndex = -1;
            if (this.ignoreValueChange) {
                this.ignoreValueChange = false;
                return;
            }
            if (q === '' || q.length < this.options.minChars) {
                this.hide();
            } else {
                this.getSuggestions(q);
            }
        },

        getQuery: function(val) {
            var d = this.options.delimiter;
            if (!d)     
                return $.trim(val);
            var arr = val.split(d);
            return $.trim(arr[arr.length - 1]);
        },

        getSuggestionsLocal: function(q) {
            var arr = this.options.lookup;
            var len = arr.suggestions.length;
            var ret = { suggestions:[], data:[] };
            q = q.toLowerCase();
            for(var i=0; i< len; i++) {
                val = arr.suggestions[i];
                if(val.toLowerCase().indexOf(q) === 0) {
                    ret.suggestions.push(val);
                    ret.data.push(arr.data[i]);
                }
            }
            return ret;
        },
    
        getSuggestions: function(q) {
            var cr = this.isLocal ? this.getSuggestionsLocal(q) : this.cachedResponse[q];

            if (cr) {
                this.suggest(cr.data);
            } else if (!this.isBadQuery(q)) {
                var self = this;
                self.options.params.query = q;
                $.ajax(this.url, {
                            type: this.options.remoteQueryType,
                            success: function(response) { self.processResponse(response, q); },
                            data: this.options.params,
                            dataType: this.options.remoteDataType
                        });
            }
        },

        isBadQuery: function(q) {
            var i = this.badQueries.length;
            while (i--) {
                if (q.indexOf(this.badQueries[i]) === 0) { 
                    return true; 
                }
            }
            return false;
        },

        hide: function() {
            this.enabled = false;
            this.selectedIndex = -1;
            this.container.hide();
        },

        suggest: function(data) {
            this.container.hide().empty();

            if (data.length === 0) 
                return;
            
            var self  = this;
            var fmt   = this.options.formatItem;
            var show  = this.options.showItem;
            var query = this.getQuery(this.currentValue);

            var fOver  = function(idx) { return function(e) { return self.activate(idx, self.suggestions[idx]); } };
            var fClick = function(idx) { return function(e) { return self.select(idx, self.suggestions[idx]); } };

            this.suggestions = [];

            for (var i = 0; i < data.length; i++) {
                var item = data[i];

                var div = $('<div>' + fmt(data[i], query) + '</div>');
                if (this.selectedIndex == i)
                    div.addClass('selected');
                div.bind({
                    mouseover: fOver(i),
                    click: fClick(i)
                });
                this.container.append(div);

                this.suggestions.push(show(data[i], query));
            }
            
            this.enabled = true;
            this.container.show();
        },

        processResponse: function(response, query) {
            if (!$.isArray(response.data)) 
                response.data = [];

            if (this.options.useCache) {
                this.cachedResponse[query] = response;
                if (response.data.length === 0) 
                    this.badQueries.push(query);
            }
            if (query === this.getQuery(this.currentValue)) {
                this.suggest(response.data); 
            }
        },

        activate: function(index, item) {
            var divs = this.container.children();
            // Clear previous selection:
            if (this.selectedIndex !== -1 && divs.length > this.selectedIndex) {
                $(divs.get(this.selectedIndex)).removeClass();
            }

            var activeItem;
            this.selectedIndex = index;
            if (this.selectedIndex !== -1 && divs.length > this.selectedIndex) {
                activeItem = divs.get(this.selectedIndex);
                $(activeItem).addClass('selected');
            }
            return activeItem;
        },

        deactivate: function(div, index) {
            div.className = '';
            if (this.selectedIndex === index) { this.selectedIndex = -1; }
        },

        select: function(i, item) {
            this.el.val(item);
            this.hide();

            this.ignoreValueChange = true;
            this.onSelect(i, item);

            if (this.options.autoSubmit) {
                this.el.closest('form').submit();
            }
            return true;
        },

        moveUp: function() {
            if (this.selectedIndex === -1) 
                return;
            if (this.selectedIndex === 0) {
                this.container.children().get(0).className = '';
                this.selectedIndex = -1;
                this.el.val(this.currentValue);
            } else {
                this.adjustScroll(this.selectedIndex - 1);
            }
        },

        moveDown: function() {
            if (this.selectedIndex === (this.suggestions.length - 1)) 
                return;
            this.adjustScroll(this.selectedIndex + 1);
        },

        adjustScroll: function(i) {
            var activeItem = this.activate(i);
            var offsetTop = activeItem.offsetTop;
            var upperBound = this.container.scrollTop();
            var lowerBound = upperBound + this.options.maxHeight - 25;

            if (offsetTop < upperBound) {
                this.container.scrollTop(offsetTop);
            } else if (offsetTop > lowerBound) {
                this.container.scrollTop(offsetTop - this.options.maxHeight + 25);
            }
        },

        onSelect: function(i, item) {
            var fn = this.options.onSelect;

            this.el.val(this.getValue(item));
            if ($.isFunction(fn)) 
                fn(item, this.el);
        },
    
        getValue: function(value){
            var del = this.options.delimiter;
            if (!del) 
                return value;
            var currVal = this.currentValue;
            var arr = currVal.split(del);
            if (arr.length === 1) 
                return value;
            return currVal.substr(0, currVal.length - arr[arr.length - 1].length) + value;
        },

        showItem: function(value, query) {
            return value;
        },

        formatItem: function(value, query) {
            var pattern = '(' + query.replace(reEscape, '\\$1') + ')';
            return value.replace(new RegExp(pattern, 'gi'), '<strong>$1<\/strong>');
        }
    }

}(jQuery));
