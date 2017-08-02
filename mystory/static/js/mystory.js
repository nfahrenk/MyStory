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

(function() {
  var CssSelectorGenerator, root,
    indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  CssSelectorGenerator = (function() {
    CssSelectorGenerator.prototype.default_options = {
      selectors: ['id', 'class', 'tag', 'nthchild']
    };

    function CssSelectorGenerator(options) {
      if (options == null) {
        options = {};
      }
      this.options = {};
      this.setOptions(this.default_options);
      this.setOptions(options);
    }

    CssSelectorGenerator.prototype.setOptions = function(options) {
      var key, results, val;
      if (options == null) {
        options = {};
      }
      results = [];
      for (key in options) {
        val = options[key];
        if (this.default_options.hasOwnProperty(key)) {
          results.push(this.options[key] = val);
        } else {
          results.push(void 0);
        }
      }
      return results;
    };

    CssSelectorGenerator.prototype.isElement = function(element) {
      return !!((element != null ? element.nodeType : void 0) === 1);
    };

    CssSelectorGenerator.prototype.getParents = function(element) {
      var current_element, result;
      result = [];
      if (this.isElement(element)) {
        current_element = element;
        while (this.isElement(current_element)) {
          result.push(current_element);
          current_element = current_element.parentNode;
        }
      }
      return result;
    };

    CssSelectorGenerator.prototype.getTagSelector = function(element) {
      return this.sanitizeItem(element.tagName.toLowerCase());
    };

    CssSelectorGenerator.prototype.sanitizeItem = function(item) {
      var characters;
      characters = (item.split('')).map(function(character) {
        if (character === ':') {
          return "\\" + (':'.charCodeAt(0).toString(16).toUpperCase()) + " ";
        } else if (/[ !"#$%&'()*+,.\/;<=>?@\[\\\]^`{|}~]/.test(character)) {
          return "\\" + character;
        } else {
          return escape(character).replace(/\%/g, '\\');
        }
      });
      return characters.join('');
    };

    CssSelectorGenerator.prototype.getIdSelector = function(element) {
      var id, sanitized_id;
      id = element.getAttribute('id');
      if ((id != null) && (id !== '') && !(/\s/.exec(id)) && !(/^\d/.exec(id))) {
        sanitized_id = "#" + (this.sanitizeItem(id));
        if (element.ownerDocument.querySelectorAll(sanitized_id).length === 1) {
          return sanitized_id;
        }
      }
      return null;
    };

    CssSelectorGenerator.prototype.getClassSelectors = function(element) {
      var class_string, item, result;
      result = [];
      class_string = element.getAttribute('class');
      if (class_string != null) {
        class_string = class_string.replace(/\s+/g, ' ');
        class_string = class_string.replace(/^\s|\s$/g, '');
        if (class_string !== '') {
          result = (function() {
            var k, len, ref, results;
            ref = class_string.split(/\s+/);
            results = [];
            for (k = 0, len = ref.length; k < len; k++) {
              item = ref[k];
              results.push("." + (this.sanitizeItem(item)));
            }
            return results;
          }).call(this);
        }
      }
      return result;
    };

    CssSelectorGenerator.prototype.getAttributeSelectors = function(element) {
      var attribute, blacklist, k, len, ref, ref1, result;
      result = [];
      blacklist = ['id', 'class'];
      ref = element.attributes;
      for (k = 0, len = ref.length; k < len; k++) {
        attribute = ref[k];
        if (ref1 = attribute.nodeName, indexOf.call(blacklist, ref1) < 0) {
          result.push("[" + attribute.nodeName + "=" + attribute.nodeValue + "]");
        }
      }
      return result;
    };

    CssSelectorGenerator.prototype.getNthChildSelector = function(element) {
      var counter, k, len, parent_element, sibling, siblings;
      parent_element = element.parentNode;
      if (parent_element != null) {
        counter = 0;
        siblings = parent_element.childNodes;
        for (k = 0, len = siblings.length; k < len; k++) {
          sibling = siblings[k];
          if (this.isElement(sibling)) {
            counter++;
            if (sibling === element) {
              return ":nth-child(" + counter + ")";
            }
          }
        }
      }
      return null;
    };

    CssSelectorGenerator.prototype.testSelector = function(element, selector) {
      var is_unique, result;
      is_unique = false;
      if ((selector != null) && selector !== '') {
        result = element.ownerDocument.querySelectorAll(selector);
        if (result.length === 1 && result[0] === element) {
          is_unique = true;
        }
      }
      return is_unique;
    };

    CssSelectorGenerator.prototype.getAllSelectors = function(element) {
      var result;
      result = {
        t: null,
        i: null,
        c: null,
        a: null,
        n: null
      };
      if (indexOf.call(this.options.selectors, 'tag') >= 0) {
        result.t = this.getTagSelector(element);
      }
      if (indexOf.call(this.options.selectors, 'id') >= 0) {
        result.i = this.getIdSelector(element);
      }
      if (indexOf.call(this.options.selectors, 'class') >= 0) {
        result.c = this.getClassSelectors(element);
      }
      if (indexOf.call(this.options.selectors, 'attribute') >= 0) {
        result.a = this.getAttributeSelectors(element);
      }
      if (indexOf.call(this.options.selectors, 'nthchild') >= 0) {
        result.n = this.getNthChildSelector(element);
      }
      return result;
    };

    CssSelectorGenerator.prototype.testUniqueness = function(element, selector) {
      var found_elements, parent;
      parent = element.parentNode;
      found_elements = parent.querySelectorAll(selector);
      return found_elements.length === 1 && found_elements[0] === element;
    };

    CssSelectorGenerator.prototype.testCombinations = function(element, items, tag) {
      var item, k, l, len, len1, ref, ref1;
      ref = this.getCombinations(items);
      for (k = 0, len = ref.length; k < len; k++) {
        item = ref[k];
        if (this.testUniqueness(element, item)) {
          return item;
        }
      }
      if (tag != null) {
        ref1 = items.map(function(item) {
          return tag + item;
        });
        for (l = 0, len1 = ref1.length; l < len1; l++) {
          item = ref1[l];
          if (this.testUniqueness(element, item)) {
            return item;
          }
        }
      }
      return null;
    };

    CssSelectorGenerator.prototype.getUniqueSelector = function(element) {
      var found_selector, k, len, ref, selector_type, selectors;
      selectors = this.getAllSelectors(element);
      ref = this.options.selectors;
      for (k = 0, len = ref.length; k < len; k++) {
        selector_type = ref[k];
        switch (selector_type) {
          case 'id':
            if (selectors.i != null) {
              return selectors.i;
            }
            break;
          case 'tag':
            if (selectors.t != null) {
              if (this.testUniqueness(element, selectors.t)) {
                return selectors.t;
              }
            }
            break;
          case 'class':
            if ((selectors.c != null) && selectors.c.length !== 0) {
              found_selector = this.testCombinations(element, selectors.c, selectors.t);
              if (found_selector) {
                return found_selector;
              }
            }
            break;
          case 'attribute':
            if ((selectors.a != null) && selectors.a.length !== 0) {
              found_selector = this.testCombinations(element, selectors.a, selectors.t);
              if (found_selector) {
                return found_selector;
              }
            }
            break;
          case 'nthchild':
            if (selectors.n != null) {
              return selectors.n;
            }
        }
      }
      return '*';
    };

    CssSelectorGenerator.prototype.getSelector = function(element) {
      var all_selectors, item, k, l, len, len1, parents, result, selector, selectors;
      all_selectors = [];
      parents = this.getParents(element);
      for (k = 0, len = parents.length; k < len; k++) {
        item = parents[k];
        selector = this.getUniqueSelector(item);
        if (selector != null) {
          all_selectors.push(selector);
        }
      }
      selectors = [];
      for (l = 0, len1 = all_selectors.length; l < len1; l++) {
        item = all_selectors[l];
        selectors.unshift(item);
        result = selectors.join(' > ');
        if (this.testSelector(element, result)) {
          return result;
        }
      }
      return null;
    };

    CssSelectorGenerator.prototype.getCombinations = function(items) {
      var i, j, k, l, ref, ref1, result;
      if (items == null) {
        items = [];
      }
      result = [[]];
      for (i = k = 0, ref = items.length - 1; 0 <= ref ? k <= ref : k >= ref; i = 0 <= ref ? ++k : --k) {
        for (j = l = 0, ref1 = result.length - 1; 0 <= ref1 ? l <= ref1 : l >= ref1; j = 0 <= ref1 ? ++l : --l) {
          result.push(result[j].concat(items[i]));
        }
      }
      result.shift();
      result = result.sort(function(a, b) {
        return a.length - b.length;
      });
      result = result.map(function(item) {
        return item.join('');
      });
      return result;
    };

    return CssSelectorGenerator;

  })();

  if (typeof define !== "undefined" && define !== null ? define.amd : void 0) {
    define([], function() {
      return CssSelectorGenerator;
    });
  } else {
    root = typeof exports !== "undefined" && exports !== null ? exports : this;
    root.CssSelectorGenerator = CssSelectorGenerator;
  }

}).call(this);
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
YS.timestamp = function() {
    dateObj = new Date();
    return dateObj.toUTCString() + ' ' + dateObj.getUTCMilliseconds();
};
YS.baseUrl = window.location.protocol + "//" + window.location.hostname + (window.location.port == "" ? "" : ":" + window.location.port);
YS.url = window.location.href;

YS.newSession = function() {
    var sessionForm = new FormData();
    sessionForm.append('baseUrl', YS.baseUrl);
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
};

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
};

YS.newEvents = function() {
    var eventForm = new FormData();
    eventForm.append('url', YS.url);    
    eventForm.append('actionEvents', JSON.stringify(YS.actionEvents));
    YS.actionEvents = [];
    eventForm.append('modifiedAttributes', JSON.stringify(YS.modifiedAttributes));
    YS.modifiedAttributes = [];
    eventForm.append('insertedOrDeleted', JSON.stringify(YS.insertedOrDeleted));
    YS.insertedOrDeleted = [];
    fetch(YS.BASE_URL + "/record/" + localStorage.getItem('sessionId'), {
        method: "POST",
        body: eventForm
    });
};

YS.record = function() {
    (function (global) {
        if ( !global.Event && !('keys' in Object) && !('bind' in Function) ) { return; }

        var eventProto = Event.prototype,
            ALL_EVENTS = ['click', 'dblclick', 'contextmenu', 'mousedown', 'mouseup', 'keydown', 'keypress', 'keyup'],
            logEvent = function ( evt ) {
                var isKeyboardEvent = evt.type == 'keypress' || evt.type == 'keyup' || evt.type == 'keydown';
                var isHoldKey = evt.key == 'Control' || evt.key == 'Shift' || evt.key == 'Alt';
                if ((evt.type == 'keypress' && !isHoldKey) || (isKeyboardEvent && isHoldKey)) {
                    YS.actionEvents.push({'eventType': actionEnum[evt.type], 'key': evt.key, 'timestamp': YS.timestamp()});
                } else if (!isKeyboardEvent) {
                    console.log(evt.target);
                    my_selector_generator = new CssSelectorGenerator();
                    var targetSelector = my_selector_generator.getSelector(evt.target);
                    YS.actionEvents.push({'eventType': actionEnum[evt.type], 'timestamp': YS.timestamp(), 'target': targetSelector});
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

    prevX = 0;
    prevY = 0;
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
            if (pos && (prevX != pos.x || prevY != pos.y)) {
                YS.actionEvents.push({'eventType': actionEnum.mousemove, x: pos.x, y: pos.y, timestamp: YS.timestamp()});
            } else if (pos) {
                prevX = pos.x;
                prevY = pos.y;
            }
        }
    })();

    window.setInterval(function() {
        if (YS.body == '') {
            YS.newEvents();
        }
    }, 2000);
};

YS.newIdentity = function(identity) {
    var identityForm = new FormData();
    identityForm.append('url', YS.url);
    identityForm.append('identifier', identity);
    fetch(YS.BASE_URL + "/initialize/" + localStorage.getItem('sessionId'), {
        method: "POST",
        body: identityForm
    });
};

YS.main = function() {
    if (!localStorage.getItem('sessionId')) {
        YS.newSession();
    }
    console.log(localStorage.getItem('sessionId'));
    YS.newPage();
    YS.record();
};

YS.main();

// Track event

// Track DOM changes
/*
var inserted_or_deleted = [],
    modified_attributes = [];

var inserted_or_deleted_callback = function(allmutations) {
    allmutations.map( function(mr) {
        inserted_or_deleted.push({timestamp: Date.now(), type: mr.type, target: mr.targer});
    });
},
inserted_or_deleted_observer = new MutationObserver(inserted_or_deleted_callback),
inserted_or_deleted_options = {
    'childList': true,
    'subtree': true
};
var modified_attributes_callback = function(allmutations){
    allmutations.map( function(mr){
        modified_attributes.push({timestamp: Date.now(), type: mr.oldValue});
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