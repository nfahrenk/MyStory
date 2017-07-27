/*
// Get links to all images
var images = [];
for (var i = 0; i < document.images.length; i++) {
    images.push(document.images[i].src);
}

// Get links to all css files
var css = [], links = document.getElementsByTagName('link');
for (var i = 0; i < links.length; i++) {
    css.push(links[i].href);
}
*/

YS.body = new XMLSerializer().serializeToString(document);
var actionEnum = {
    click: 0,
    dblclick: 1,
    contextmenu: 2,
    mousedown: 3,
    mouseup: 4,
    keydown: 5,
    keyup: 6,
    keypress: 7,
    mousemove: 8
};
YS.actionEvents = [];
YS.modifiedAttributes = [];
YS.insertedOrDeleted = [];
YS.timestamp = function() {return (new Date()).toUTCString();};
YS.baseUrl = window.location.protocol + "//" + window.location.hostname + (window.location.port == "" ? "" : ":" + window.location.port);
YS.url = window.location.href;

YS.newSession = function() {
    var sessionForm = new FormData();
    sessionForm.append('baseUrl', YS.baseUrl;
    sessionForm.append('timestamp', YS.timestamp());
    fetch(YS.BASE_URL + "/start", {
        method: "POST",
        body: sessionForm
    }).then(function (response) {        
        var contentType = response.headers.get("content-type");
        if(contentType && contentType.includes("application/json")) {
          return response.json();
        }
        throw new TypeError("Oops, we haven't got JSON!");
    }).then(function (json) {
        localStorage.setItem('sessionId', json.sessionId);
    });
}

YS.newPage = function() {
    var w = window,
        d = document,
        e = d.documentElement,
        g = d.getElementsByTagName('body')[0],
        x = w.innerWidth || e.clientWidth || g.clientWidth,
        y = w.innerHeight|| e.clientHeight|| g.clientHeight;
    var pageForm = new FormData();
    pageForm.append('url', YS.url);
    pageForm.append('screenWidth', x);
    pageForm.append('screenHeight', y);
    pageForm.append('timestamp', YS.timestamp());
    pageForm.append('text', YS.body);    
    var firstTime = true;
    fetch(YS.BASE_URL + "/page/" + localStorage.getItem('sessionId'), {
        method: "POST",
        body: pageForm
    }).then(function (response) {
        if (!response.ok && firstTime) {
            YS.newSession();
            YS.newPage();
        } else if (response.ok) {
            YS.body = '';
        }
        firstTime = false;
    });
}

YS.newEvents = function() {
    var eventForm = new FormData();
    eventForm.append('url', YS.url);
    eventForm.append('actionEvents', YS.actionEvents);
    YS.actionEvents = [];
    eventForm.append('modifiedAttributes', YS.modifiedAttributes);
    YS.modifiedAttributes = [];
    eventForm.append('insertedOrDeleted', YS.insertedOrDeleted);
    YS.insertedOrDeleted = [];
    fetch(YS.BASE_URL + "/record/" + localStorage.getItem('sessionId'), {
        method: "POST",
        body: eventForm
    });
}

YS.record = function() {
    (function (global) {
        if ( !global.Event && !('keys' in Object) && !('bind' in Function) ) { return }

        var eventProto = Event.prototype,
            ALL_EVENTS = ['click', 'dblclick', 'contextmenu', 'mousedown', 'mouseup', 'keydown', 'keypress', 'keyup'],
            PHASES = [ '', 'CAPTURING_PHASE', 'AT_TARGET', 'BUBBLING_PHASE' ],
            logEvent = function ( evt ) {
                if (evt.type == 'keypress') {
                    YS.actionEvents.append({'eventType': evt.type, 'key': evt.key, 'timestamp': YS.timestamp()});
                } else {
                    YS.actionEvents.append({'eventType': evt.type, 'timestamp': YS.timestamp()});
                }                
            },
            bindEvents = function (eventName) {
                unbindEvents(eventName);
                this.addEventListener( eventName, logEvent, false);
            },
            unbindEvents = function (eventName) {
                this.removeEventListener( eventName, logEvent, false);
            };
        global.EventMonitor = {
            start: function ( elm, eventType ) {
                var binder = bindEvents.bind(elm);
                if(!eventType) {
                    ALL_EVENTS.forEach( binder );
                } else {
                    binder(eventType);
                }
            },
            stop: function ( elm, eventType ) {
                var unbinder = unbindEvents.bind(elm);
                if(!eventType) {
                    ALL_EVENTS.forEach( unbinder );
                } else {
                    unbinder(eventType);
                }
            }
        };
    }(YS));
    YS.EventMonitor.start();

    (function() {
        var mousePos;

        document.onmousemove = handleMouseMove;
        setInterval(getMousePosition, 300); // setInterval repeats every X ms

        function handleMouseMove(event) {
            var dot, eventDoc, doc, body, pageX, pageY;

            event = event || window.event; // IE-ism

            // If pageX/Y aren't available and clientX/Y are,
            // calculate pageX/Y - logic taken from jQuery.
            // (This is to support old IE)
            if (event.pageX == null && event.clientX != null) {
                eventDoc = (event.target && event.target.ownerDocument) || document;
                doc = eventDoc.documentElement;
                body = eventDoc.body;

                event.pageX = event.clientX +
                  (doc && doc.scrollLeft || body && body.scrollLeft || 0) -
                  (doc && doc.clientLeft || body && body.clientLeft || 0);
                event.pageY = event.clientY +
                  (doc && doc.scrollTop  || body && body.scrollTop  || 0) -
                  (doc && doc.clientTop  || body && body.clientTop  || 0 );
            }

            mousePos = {
                x: event.pageX,
                y: event.pageY
            };
        }
        function getMousePosition() {
            var pos = mousePos;
            if (pos) {
                YS.actionEvents.append({eventType: actionEnum.mousemove, x: pos.x, y: pos.y, timestamp: YS.timestamp()});
            }
        }
    })();

    window.setInterval(function() {
        if (YS.body == '') {
            YS.newEvents();
        }
    }, 5000);
}

YS.newIdentity = function(identity) {
    var identityForm = new FormData();
    identityForm.append('url', FS.url);
    identityForm.append('identifier', identity);
    fetch(YS.BASE_URL + "/initialize/" + localStorage.getItem('sessionId'), {
        method: "POST",
        body: identityForm
    });
}

YS.main = function() {
    if (localStorage.getItem('sessionId') == null) {
        YS.newSession();
    }
    YS.newPage();
    YS.record();
}

// Track event

// Track DOM changes
/*
var inserted_or_deleted = [],
    modified_attributes = [];

var inserted_or_deleted_callback = function(allmutations) {
    allmutations.map( function(mr) {
        inserted_or_deleted.append({timestamp: Date.now(), type: mr.type, target: mr.targer});
    });
},
inserted_or_deleted_observer = new MutationObserver(inserted_or_deleted_callback),
inserted_or_deleted_options = {
    'childList': true,
    'subtree': true
};
var modified_attributes_callback = function(allmutations){
    allmutations.map( function(mr){
        modified_attributes.append({timestamp: Date.now(), type: mr.oldValue});
    });
},
modified_attributes_observer = new MutationObserver(modified_attributes_callback),
modified_attributes_options = {
    'attributes': true,
    'attributeOldValue': true,
    'subtree': true
};

inserted_or_deleted_observer.observe(document.body, inserted_or_deleted_options);
modified_attributes_observer.observe(document.body, modified_attributes_options);
*/