var preProc = {
  apply:  function(c) {
    // process the document before anything else is done
    var refs = document.querySelectorAll('adef') ;
    for (var i = 0; i < refs.length; i++) {
        var item = refs[i];
        var p = item.parentNode ;
        var con = item.innerHTML ;
        var sp = document.createElement( 'dfn' ) ;
        var tit = item.getAttribute('title') ;
        if (!tit) {
            tit = con;
        }
        sp.className = 'adef' ;
        sp.title=tit ;
        sp.innerHTML = con ;
        p.replaceChild(sp, item) ;
    }
    refs = document.querySelectorAll('aref') ;
    for (var i = 0; i < refs.length; i++) {
        var item = refs[i];
        var p = item.parentNode ;
        var con = item.innerHTML ;
        var sp = document.createElement( 'a' ) ;
        sp.className = 'aref' ;
        sp.setAttribute('title', con);
        sp.innerHTML = '@'+con ;
        p.replaceChild(sp, item) ;
    }
    // local datatype references
    refs = document.querySelectorAll('ldtref') ;
    for (var i = 0; i < refs.length; i++) {
        var item = refs[i];
        if (!item) continue ;
        var p = item.parentNode ;
        var con = item.innerHTML ;
        var ref = item.getAttribute('title') ;
        if (!ref) {
            ref = item.textContent ;
        }
        if (ref) {
            ref = ref.replace(/\n/g, '_') ;
            ref = ref.replace(/\s+/g, '_') ;
        }
        var sp = document.createElement( 'a' ) ;
        sp.className = 'datatype';
        sp.title = ref ;
        sp.innerHTML = con ;
        p.replaceChild(sp, item) ;
    }
    // external datatype references
    refs = document.querySelectorAll('dtref') ;
    for (var i = 0; i < refs.length; i++) {
        var item = refs[i];
        if (!item) continue ;
        var p = item.parentNode ;
        var con = item.innerHTML ;
        var ref = item.getAttribute('title') ;
        if (!ref) {
            ref = item.textContent ;
        }
        if (ref) {
            ref = ref.replace(/\n/g, '_') ;
            ref = ref.replace(/\s+/g, '_') ;
        }
        var sp = document.createElement( 'a' ) ;
        sp.className = 'externalDFN';
        sp.title = ref ;
        sp.innerHTML = con ;
        p.replaceChild(sp, item) ;
    }
    // now do terms
    refs = document.querySelectorAll('tdef') ;
    for (var i = 0; i < refs.length; i++) {
        var item = refs[i];
        if (!item) continue ;
        var p = item.parentNode ;
        var con = item.innerHTML ;
        var ref = item.getAttribute('title') ;
        if (!ref) {
            ref = item.textContent ;
        }
        if (ref) {
            ref = ref.replace(/\n/g, '_') ;
            ref = ref.replace(/\s+/g, '_') ;
        }
        var sp = document.createElement( 'dfn' ) ;
        sp.title = ref ;
        sp.innerHTML = con ;
        p.replaceChild(sp, item) ;
    }
    // now term references
    refs = document.querySelectorAll('tref') ;
    for (var i = 0; i < refs.length; i++) {
        var item = refs[i];
        if (!item) continue ;
        var p = item.parentNode ;
        var con = item.innerHTML ;
        var ref = item.getAttribute('title') ;
        if (!ref) {
            ref = item.textContent ;
        }
        if (ref) {
            ref = ref.replace(/\n/g, '_') ;
            ref = ref.replace(/\s+/g, '_') ;
        }

        var sp = document.createElement( 'a' ) ;
        var id = item.textContent ;
        sp.className = 'tref' ;
        sp.title = ref ;
        sp.innerHTML = con ;
        p.replaceChild(sp, item) ;
    }
  }
};

function updateExample(doc, content) {
    // perform transformations to make it render and prettier
    content = content.replace(/<!--/, '');
    content = content.replace(/-->/, '');
    content = doc._esc(content);
    content = content.replace(/\*\*\*\*([^*]*)\*\*\*\*/g, '<span class="hilite">$1</span>') ;
    return content ;
}

function updateDTD(doc, content) {
    // perform transformations to 
    // make it render and prettier
    content = '<pre class="dtd">' + doc._esc(content) + '</pre>';
    content = content.replace(/!ENTITY % ([^ \t\r\n]*)/g, '!ENTITY <span class="entity">% $1</span>');
    content = content.replace(/!ELEMENT ([^ \t$]*)/mg, '!ELEMENT <span class="element">$1</span>');
    return content;
}

function updateSchema(doc, content) {
    // perform transformations to 
    // make it render and prettier
    content = '<pre class="dtd">' + doc._esc(content) + '</pre>';
    content = content.replace(/&lt;xs:element\s+name=&quot;([^&]*)&quot;/g, '&lt;xs:element name="<span class="element" id="schema_element_$1">$1</span>"') ;
    return content;
}

function updateTTL(doc, content) {
    // perform transformations to 
    // make it render and prettier
    content = '<pre class="sh_sourceCode">' + doc._esc(content) + '</pre>';
    content = content.replace(/@prefix/g, '<span class="sh_keyword">@prefix</span>');
    return content;
}

