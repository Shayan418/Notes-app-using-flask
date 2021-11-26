//source: https://codepen.io/chriscoyier/pen/XWbqpzP

window.onload = function () {
    function calcHeight(value) {
        let numberOfLineBreaks = (value.match(/\n/g) || []).length;
        if (numberOfLineBreaks < 8)
            numberOfLineBreaks = 8;
        // min-height + lines x line-height + padding + border
        let newHeight = 24 + numberOfLineBreaks * 24 + 12 + 1.996;
        return newHeight;
    }
    let textarea = document.getElementById('resize-ta');
    
    textarea.addEventListener("keyup", () => {
        var newHeight = calcHeight(textarea.value)
        textarea.style.height = calcHeight(textarea.value) + "px";
        window.scrollTo(0,99999);
    });
}
