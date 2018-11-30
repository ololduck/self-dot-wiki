///////////////////////////////////////////////////////////////////////////////
//
// AccessKey Underlining Library v0.4
//
// Copyright (c) 2005 Data Connection Ltd.
//
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the "Software"),
// to deal in the Software without restriction, including without limitation
// the rights to use, copy, modify, merge, publish, distribute, sublicense,
// and/or sell copies of the Software, and to permit persons to whom the
// Software is furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
// DEALINGS IN THE SOFTWARE.
//
// Maintainer: gerv@gerv.net; http://www.gerv.net/software/aul/
//
// CHANGELOG:
//
// v0.1: initial version (2005-02-16)
// v0.2: made it validate, which needs nasty <div> hack
// v0.3: changed switching approach to something nicer, if a little less
//       cutting-edge. (2005-05-22)
// v0.4: Removed obsolete code and comments. (2005-06-26)
// v0.4.1: Added <a> elements
//
///////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////
//
// The accesskey attribute is permitted by HTML on the following elements:
// <a>, <area>, <button>, <input>, <label>, <legend> and <textarea>.
// Of those, this library underlines accesskeys for:
// <button>, <label> and <legend>.
//
// It doesn't do <a>, because to see the underline you'd have to remove
// the default underlining from links, which isn't recommended for
// usability reasons. It doesn't do the others because they don't contain
// plain text labels within themselves.
//
// This library will underline the first occurrence of the accesskey in the
// innerHTML, case-sensitively, or put it afterwards in round brackets if
// there's no match. So:
//
// - Make sure you define your accesskeys in the correct case
// - Don't put markup inside any <button>, <label> or <legend> element on
//   which you've defined an accesskey
//
// Use the following markup to include the library:
// <script type="text/javascript" src="accesskey.js"></script>
//
// This library allows for separation of content and presentation. You can
// turn off all accesskey effects in a particular stylesheet (e.g. for 
// printing using the following CSS:
// .accesskey { text-decoration: none; }
// .accesskeySurround { display: none; }
//
///////////////////////////////////////////////////////////////////////////////

addEvent(window, "load", underlineAccessKeys);

function underlineAccessKeys() {
    addMarkup(document.getElementsByTagName('button'));
    addMarkup(document.getElementsByTagName('label'));
    addMarkup(document.getElementsByTagName('legend'));
}

function addMarkup(elems) {
    var elem;
    var i = 0;

    while (elem = elems.item(i++)) {
        // These go around the key itself
        var open = "<u class='accesskey'>";
        var close = "</u>";
        var attr = elem.getAttributeNode("accesskey");

        if (attr && attr.value) {
            var innerH = elem.innerHTML;
            if (innerH.match(attr.value)) {
                // Use first exact case match
                elem.innerHTML = innerH.replace(attr.value, open + attr.value + close);
            } else {
                // No match; use brackets afterwards instead
                // Possible enhancement: deal with terminating colons better
                elem.innerHTML = innerH + "<span class='accesskeySurround'> (" +
                    open + attr.value + close + ")</span>";
            }
        }
    }
}

// This is a cross-browser function for event addition.
function addEvent(obj, evType, fn) {
    if (obj.addEventListener) {
        obj.addEventListener(evType, fn, false);
        return true;
    } else if (obj.attachEvent) {
        var r = obj.attachEvent("on" + evType, fn);
        return r;
    } else {
        alert("Event handler could not be attached");
        return false;
    }
}
