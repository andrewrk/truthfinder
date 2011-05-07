function parseForDropdowns(dom) {
    $(dom).find('.node').each(function(index, item) {
        if ($(item).attr('data-master') === '1') {
            return;
        }
        var link = $(item).find('h2 a').first();
        var node_content = $(item).find('.node-content').first();
        node_content.attr('data-shown', '0');
        $(link).click(function() {
            if ($(node_content).attr('data-shown') === '0') {
                $(node_content).attr('data-shown', '1');
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
