let keykeeper = function (elementId) {
    /*
     * generate access keys on page links
     *
     */
    let e = document.getElementsByTagName('body')[0];
    keykeeper.removeHardCodedFromAvailable();
    if (elementId !== undefined)
        e = document.getElementById(elementId);
    let listOfLinks = e.getElementsByTagName('a');
    for (let i = 0; i < listOfLinks.length; i++) {
        let elem = listOfLinks[i];
        if (keykeeper.links.has(elem.href))
            elem.accessKey = keykeeper.links.get(elem.href);
        else {
            for (let j = 0; j < keykeeper.available.length; j++) {
                //for every letter inside, choose one that is in the word
                if (elem.innerHTML.indexOf(keykeeper.available[j]) > -1) {
                    // we have found one! let's get it!
                    elem.accessKey = keykeeper.available[j];
                    keykeeper.links.set(elem.href, elem.accessKey);
                    // remove it from available list
                    keykeeper.available = keykeeper.available.replace(keykeeper.available[j], '');
                    break;
                }
            }
            // if we arrive here, we did not find any suitable letter, or we found one.
            if (elem.accessKey === undefined) {
                // if we arrive here, we did not find any suitable letter.
                // let's try a fallback by picking the first letter available
                if (keykeeper.available.length === 0) {
                    console.log('Ran out of accessKeys to attribute!');
                    break; //it doesn't make any sense to keep trying, even other links
                }
                elem.accessKey = keykeeper.available[0];
                keykeeper.available = keykeeper.available.replace(keykeeper.available[0], '');
            }
        }
    }
    addMarkup(listOfLinks);
};
keykeeper.available = 'abcdefghijklmnopqrstuvwxyz';
keykeeper.removeHardCodedFromAvailable = function () {
    const elems = document.querySelectorAll('[accesskey]');
    for (let elem in elems) {
        if (elem.accessKey in keykeeper.available) {
            keykeeper.available = keykeeper.available.replace(elem.accessKey, '');
        }
    }
};
keykeeper.links = new Map();