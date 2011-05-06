/**
 * 
 * @param {Object} divName : the div id to replace with the rich text editor
 */
function setupRichTextEditor(divName, photologue){
	YAHOO.util.Dom.addClass(document.body,'yui-skin-sam');
	var params = {}
	params['divName'] = divName;
	if (photologue == "True"){
		use_photologue = true;	
	}
	else{
		use_photologue = false;
	}
	//register listener for click on image url, IF using photologue
	if (use_photologue) {
		YAHOO.util.Event.addListener("id_content_insertimage_url", "click", selectImage);
	}
	//fire when ready
	YAHOO.util.Event.onDOMReady(startRichText, params);
}

function startRichText(event,scope,params) {
    var Dom = YAHOO.util.Dom,
        Event = YAHOO.util.Event;
    
    var myConfig = {
        height: '200px',
        width: '700px',
        animate: true,
        dompath: true,
        focusAtStart: false,
		handleSubmit: true,
		autoHeight:true
    };
	
    var state = 'off';
    var myEditor = new YAHOO.widget.Editor(params['divName'], myConfig);
    myEditor.on('toolbarLoaded', function() {
        var codeConfig = {
            type: 'push', label: 'Edit HTML Code', value: 'editcode'
        };
        this.toolbar.addButtonToGroup(codeConfig, 'insertitem');
        
        this.toolbar.on('editcodeClick', function() {
            var ta = this.get('element'),
                iframe = this.get('iframe').get('element');
 
            if (state == 'on') {
                state = 'off';
                this.toolbar.set('disabled', false);
                this.setEditorHTML(ta.value);
                if (!this.browser.ie) {
                    this._setDesignMode('on');
                }
 
                Dom.removeClass(iframe, 'editor-hidden');
                Dom.addClass(ta, 'editor-hidden');
                this.show();
                this._focusWindow();
            } else {
                state = 'on';
                this.cleanHTML();
                Dom.addClass(iframe, 'editor-hidden');
                Dom.removeClass(ta, 'editor-hidden');
                this.toolbar.set('disabled', true);
                this.toolbar.getButtonByValue('editcode').set('disabled', false);
                this.toolbar.selectButton('editcode');
                this.dompath.innerHTML = 'Editing HTML Code';
                this.hide();
            }
            return false;
        }, this, true);
 
        this.on('cleanHTML', function(ev) {
            this.get('element').value = ev.html;
        }, this, true);
        
        this.on('afterRender', function() {
            var wrapper = this.get('editor_wrapper');
            wrapper.appendChild(this.get('element'));
            this.setStyle('width', '100%');
            this.setStyle('height', '100%');
            this.setStyle('visibility', '');
            this.setStyle('top', '');
            this.setStyle('left', '');
            this.setStyle('position', '');
 
            this.addClass('editor-hidden');
        }, this, true);
    }, myEditor, true);
    myEditor.render();
}


//on url click, show popup window for photo selection form
function selectImage(ev){
	win = window.open('/richtext/choose_photo/', 'IMAGE_BROWSER', 'left=20,top=20,width=850,height=600,toolbar=0,resizable=0,status=0');
	//catch popup blocker
	if(!win){
		alert("Please disable your popup blocker");
	}
}

function populateURL(newURL)
{
	document.getElementById("id_content_insertimage_url").value = newURL;
}
