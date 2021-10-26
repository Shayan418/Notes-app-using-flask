window.onload = function () {
    function calcHeight(value) {
        let numberOfLineBreaks = (value.match(/\n/g) || []).length;
        // min-height + lines x line-height + padding + border
        let newHeight = 24 + numberOfLineBreaks * 24 + 13;
        return newHeight;
    }
    let textarea = document.getElementById('resize-ta');
    
    textarea.addEventListener("keyup", () => {
        var newHeight = calcHeight(textarea.value)
        console.log(newHeight);
        window.scrollTo(0,99999);
        textarea.style.height = calcHeight(textarea.value) + "px";
    });
}