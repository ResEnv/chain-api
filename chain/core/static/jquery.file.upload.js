// Created by Ken Leidal
// https://gist.github.com/kkleidal/5c595018ce0651be3198
(function ($) {
    var oldUpload = $.fn.upload;
    jQuery.fn.upload = function( options ) {
        if ( this.prop('tagName') !== "INPUT" || this.attr('type') !== 'file' ) {
            throw new Error("Cannot call upload function for given element type.  Only works for <input type='file' />");
        }
 
        var files = this.prop('files');
 
        var defaultCallback = function() { };
        if ( ! options ) options = {};
        if ( ! options.url ) throw new Error("File upload URL not specified.");
        if ( ! options.timeout ) options.timeout = 30000;
        if ( ! options.done ) options.done =  defaultCallback;
        if ( ! options.fail ) options.fail = defaultCallback;
        if ( ! options.always ) options.always = defaultCallback;
 
        var data = new FormData();
        $.each( files, function( key, value ) {
            data.append(key, value);
        });
 
        $.ajax({
            url: options.url,
            type: 'POST',
            timeout: options.timeout,
            data: data,
            cache: false,
            dataType: 'json',
            processData: false,
            contentType: false
        }).done( options.done )
            .fail( options.fail )
            .always( options.always );
    }
})(jQuery);
