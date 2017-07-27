// Represent page as String
var generatedSource = new XMLSerializer().serializeToString(document);

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

// Believe we need all static files that do not


// x has screen width, y has screen height
var w = window,
    d = document,
    e = d.documentElement,
    g = d.getElementsByTagName('body')[0],
    YS.x = w.innerWidth || e.clientWidth || g.clientWidth,
    YS.y = w.innerHeight|| e.clientHeight|| g.clientHeight;

var YS.sessionForm = new FormData();
YS.sessionForm.append('screenWidth', YS.x);
YS.sessionForm.append('screenHeight', YS.y);
YS.sessionForm.append('baseUrl', window.location.hostname);
YS.sessionForm.append('timestamp', (new Date()).toUTCString());
fetch("/login", {
    method: "POST",
    body: YS.sessionForm
});


// Track events

click = 0
dblclick = 1
contextmenu = 2
mousedown = 3
mouseup = 4
keydown = 5
keyup = 6
keypress = 7


(function (global) {
    if ( !global.Event && !('keys' in Object) && !('bind' in Function) ) { return }

    var eventProto = Event.prototype,
        ALL_EVENTS = ['click', 'dblclick', 'contextmenu', 'mousedown', 'mouseup', 'keydown', 'keypress', 'keyup'],
        PHASES = [ '', 'CAPTURING_PHASE', 'AT_TARGET', 'BUBBLING_PHASE' ],
        logEvent = function ( evt ) {
            console.log(evt.type, evt, PHASES[evt.eventPhase]);
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
}(window));

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
        if (!pos) {
            // We haven't seen any movement yet
        }
        else {
            console.log(pos.x, pos.y);
        }
    }
})();

// Track DOM changes
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