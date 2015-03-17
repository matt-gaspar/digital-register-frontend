if (googleAnalyticsApiKey.length > 0) {
  // Copied from Google Analytics admin page
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
   })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  // Create the analytics object for use within the whole website
  // ga('create', googleAnalyticsApiKey, 'auto');
  // for localhost testing uncomment the below line
  ga('create', googleAnalyticsApiKey,{'cookieDomain': 'none'});

  // send an initial pageview event for logging
  ga('send', 'pageview');
}

/**
* Function that tracks a click on an outbound link in Google Analytics.
* This function takes a valid URL string as an argument, and uses that URL string
* as the event label.
*/
var trackOutboundLink = function(url) {
  // to see this event in the Google Analytics website go to Behaviour >> Events >> Overview
   ga('send', 'event', 'outbound', 'click', url, {'hitCallback':
     function () {
       document.location = url;
     }
   });
}
