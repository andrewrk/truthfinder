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

function parseForNodeSearch(dom) {
    $(dom).find('input.nodesearch').each(function(index, item) {
        var name = $(item).attr('id');
        var hidden_id = name + '_hidden';

        $(item).attr('placeholder', 'Search names');

        // insert a hidden input next to it with the node id
        $(item).after('<input id="' + hidden_id +
            '" type="text" name="' + name +  '" value="" class="nodeid" placeholder="Node ID" />');
        
        $(item).autocomplete({
            source: "/ajax/search/",
            minLength: 1,
            select: function (event, ui) {
                $('#' + hidden_id).val(ui.item.id);
            }
        });
    });
}

$(document).ready(function() {
    parseForDropdowns(document);
    parseForNodeSearch(document);
});
