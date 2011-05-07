function parseForDropdowns(dom) {
    $(dom).find('.node').each(function(index, item) {
        var link = $(item).find('h2 a');
        var node_content = $(item).find('.node-content');
        var shown = false;
        $(link).click(function() {
            if (! shown) {
                shown = true;
                $.get(
                    "/ajax/node/" + $(link).attr('data-nodeid') + "/",
                    function (data) {
                        $(node_content).html(data);
                        parseForDropdowns($(node_content));
                    });
            }
            $(node_content).toggle();
            return false;
        });
    });
}

$(document).ready(function() {
    parseForDropdowns(document);
});
