from dataclasses import dataclass


@dataclass
class Header:
    name: str
    example: str
    description: str


headers = [
    {
        "section": "Authentication",
        "name": "WWW-Authenticate",
        "description": "Defines the authentication method that should be used to access a resource.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/WWW-Authenticate",
    },
    {
        "section": "Authentication",
        "name": "Authorization",
        "description": "Contains the credentials to authenticate a user-agent with a server.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Authorization",
    },
    {
        "section": "Authentication",
        "name": "Proxy-Authenticate",
        "description": "Defines the authentication method that should be used to access a resource behind a proxy server.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Proxy-Authenticate",
    },
    {
        "section": "Authentication",
        "name": "Proxy-Authorization",
        "description": "Contains the credentials to authenticate a user agent with a proxy server.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Proxy-Authorization",
    },
    {
        "section": "Caching",
        "name": "Age",
        "description": "The time, in seconds, that the object has been in a proxy cache.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Age",
    },
    {
        "section": "Caching",
        "name": "Cache-Control",
        "description": "Directives for caching mechanisms in both requests and responses.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Cache-Control",
    },
    {
        "section": "Caching",
        "name": "Clear-Site-Data",
        "description": "Clears browsing data (e.g. cookies, storage, cache) associated with the requesting website.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Clear-Site-Data",
    },
    {
        "section": "Caching",
        "name": "Expires",
        "description": "The date/time after which the response is considered stale.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Expires",
    },
    {
        "section": "Caching",
        "name": "No-Vary-Search",
        "description": "Specifies a set of rules that define how a URL's query parameters will affect cache matching. These rules dictate whether the same URL with different URL parameters should be saved as separate browser cache entries.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/No-Vary-Search",
    },
    {
        "section": "Conditionals",
        "name": "Last-Modified",
        "description": "The last modification date of the resource, used to compare several versions of the same resource. It is less accurate than ETag, but easier to calculate in some environments. Conditional requests using If-Modified-Since and If-Unmodified-Since use this value to change the behavior of the request.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Last-Modified",
    },
    {
        "section": "Conditionals",
        "name": "ETag",
        "description": "A unique string identifying the version of the resource. Conditional requests using If-Match and If-None-Match use this value to change the behavior of the request.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/ETag",
    },
    {
        "section": "Conditionals",
        "name": "If-Match",
        "description": "Makes the request conditional, and applies the method only if the stored resource matches one of the given ETags.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/If-Match",
    },
    {
        "section": "Conditionals",
        "name": "If-None-Match",
        "description": "Makes the request conditional, and applies the method only if the stored resource doesn't match any of the given ETags. This is used to update caches (for safe requests), or to prevent uploading a new resource when one already exists.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/If-None-Match",
    },
    {
        "section": "Conditionals",
        "name": "If-Modified-Since",
        "description": "Makes the request conditional, and expects the resource to be transmitted only if it has been modified after the given date. This is used to transmit data only when the cache is out of date.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/If-Modified-Since",
    },
    {
        "section": "Conditionals",
        "name": "If-Unmodified-Since",
        "description": "Makes the request conditional, and expects the resource to be transmitted only if it has not been modified after the given date. This ensures the coherence of a new fragment of a specific range with previous ones, or to implement an optimistic concurrency control system when modifying existing documents.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/If-Unmodified-Since",
    },
    {
        "section": "Conditionals",
        "name": "Vary",
        "description": "Determines how to match request headers to decide whether a cached response can be used rather than requesting a fresh one from the origin server.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Vary",
    },
    {
        "section": "Connection management",
        "name": "Connection",
        "description": "Controls whether the network connection stays open after the current transaction finishes.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Connection",
    },
    {
        "section": "Connection management",
        "name": "Keep-Alive",
        "description": "Controls how long a persistent connection should stay open.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Keep-Alive",
    },
    {
        "section": "Content negotiation",
        "name": "Accept",
        "description": "Informs the server about the types of data that can be sent back.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Accept",
    },
    {
        "section": "Content negotiation",
        "name": "Accept-Encoding",
        "description": "The encoding algorithm, usually a compression algorithm, that can be used on the resource sent back.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Accept-Encoding",
    },
    {
        "section": "Content negotiation",
        "name": "Accept-Language",
        "description": "Informs the server about the human language the server is expected to send back. This is a hint and is not necessarily under the full control of the user: the server should always pay attention not to override an explicit user choice (like selecting a language from a dropdown).",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Accept-Language",
    },
    {
        "section": "Controls",
        "name": "Expect",
        "description": "Indicates expectations that need to be fulfilled by the server to properly handle the request.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Expect",
    },
    {
        "section": "Controls",
        "name": "Max-Forwards",
        "description": "When using TRACE, indicates the maximum number of hops the request can do before being reflected to the sender.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Max-Forwards",
    },
    {
        "section": "Cookies",
        "name": "Cookie",
        "description": "Contains stored HTTP cookies previously sent by the server with the Set-Cookie header.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Cookie",
    },
    {
        "section": "Cookies",
        "name": "Set-Cookie",
        "description": "Send cookies from the server to the user-agent.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Set-Cookie",
    },
    {
        "section": "CORS",
        "name": "Access-Control-Allow-Credentials",
        "description": "Indicates whether the response to the request can be exposed when the credentials flag is true.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Credentials",
    },
    {
        "section": "CORS",
        "name": "Access-Control-Allow-Headers",
        "description": "Used in response to a preflight request to indicate which HTTP headers can be used when making the actual request.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Headers",
    },
    {
        "section": "CORS",
        "name": "Access-Control-Allow-Methods",
        "description": "Specifies the methods allowed when accessing the resource in response to a preflight request.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Methods",
    },
    {
        "section": "CORS",
        "name": "Access-Control-Allow-Origin",
        "description": "Indicates whether the response can be shared.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin",
    },
    {
        "section": "CORS",
        "name": "Access-Control-Expose-Headers",
        "description": "Indicates which headers can be exposed as part of the response by listing their names.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Access-Control-Expose-Headers",
    },
    {
        "section": "CORS",
        "name": "Access-Control-Max-Age",
        "description": "Indicates how long the results of a preflight request can be cached.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Access-Control-Max-Age",
    },
    {
        "section": "CORS",
        "name": "Access-Control-Request-Headers",
        "description": "Used when issuing a preflight request to let the server know which HTTP headers will be used when the actual request is made.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Access-Control-Request-Headers",
    },
    {
        "section": "CORS",
        "name": "Access-Control-Request-Method",
        "description": "Used when issuing a preflight request to let the server know which HTTP method will be used when the actual request is made.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Access-Control-Request-Method",
    },
    {
        "section": "CORS",
        "name": "Origin",
        "description": "Indicates where a fetch originates from.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Origin",
    },
    {
        "section": "CORS",
        "name": "Timing-Allow-Origin",
        "description": "Specifies origins that are allowed to see values of attributes retrieved via features of the Resource Timing API, which would otherwise be reported as zero due to cross-origin restrictions.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Timing-Allow-Origin",
    },
    {
        "section": "Downloads",
        "name": "Content-Disposition",
        "description": 'Indicates if the resource transmitted should be displayed inline (default behavior without the header), or if it should be handled like a download and the browser should present a "Save As" dialog.',
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Content-Disposition",
    },
    {
        "section": "Message body information",
        "name": "Content-Length",
        "description": "The size of the resource, in decimal number of bytes.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Content-Length",
    },
    {
        "section": "Message body information",
        "name": "Content-Type",
        "description": "Indicates the media type of the resource.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Content-Type",
    },
    {
        "section": "Message body information",
        "name": "Content-Encoding",
        "description": "Used to specify the compression algorithm.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Content-Encoding",
    },
    {
        "section": "Message body information",
        "name": "Content-Language",
        "description": "Describes the human language(s) intended for the audience, so that it allows a user to differentiate according to the users' own preferred language.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Content-Language",
    },
    {
        "section": "Message body information",
        "name": "Content-Location",
        "description": "Indicates an alternate location for the returned data.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Content-Location",
    },
    {
        "section": "Proxies",
        "name": "Forwarded",
        "description": "Contains information from the client-facing side of proxy servers that is altered or lost when a proxy is involved in the path of the request.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Forwarded",
    },
    {
        "section": "Proxies",
        "name": "Via",
        "description": "Added by proxies, both forward and reverse proxies, and can appear in the request headers and the response headers.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Via",
    },
    {
        "section": "Redirects",
        "name": "Location",
        "description": "Indicates the URL to redirect a page to.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Location",
    },
    {
        "section": "Request context",
        "name": "From",
        "description": "Contains an Internet email address for a human user who controls the requesting user agent.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/From",
    },
    {
        "section": "Request context",
        "name": "Host",
        "description": "Specifies the domain name of the server (for virtual hosting), and (optionally) the TCP port number on which the server is listening.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Host",
    },
    {
        "section": "Request context",
        "name": "Referer",
        "description": "The address of the previous web page from which a link to the currently requested page was followed.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Referer",
    },
    {
        "section": "Request context",
        "name": "Referrer-Policy",
        "description": "Governs which referrer information sent in the Referer header should be included with requests made.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Referrer-Policy",
    },
    {
        "section": "Request context",
        "name": "User-Agent",
        "description": "Contains a characteristic string that allows the network protocol peers to identify the application type, operating system, software vendor or software version of the requesting software user agent.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/User-Agent",
    },
    {
        "section": "Response context",
        "name": "Allow",
        "description": "Lists the set of HTTP request methods supported by a resource.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Allow",
    },
    {
        "section": "Response context",
        "name": "Server",
        "description": "Contains information about the software used by the origin server to handle the request.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Server",
    },
    {
        "section": "Range requests",
        "name": "Accept-Ranges",
        "description": "Indicates if the server supports range requests, and if so in which unit the range can be expressed.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Accept-Ranges",
    },
    {
        "section": "Range requests",
        "name": "Range",
        "description": "Indicates the part of a document that the server should return.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Range",
    },
    {
        "section": "Range requests",
        "name": "If-Range",
        "description": "Creates a conditional range request that is only fulfilled if the given etag or date matches the remote resource. Used to prevent downloading two ranges from incompatible version of the resource.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/If-Range",
    },
    {
        "section": "Range requests",
        "name": "Content-Range",
        "description": "Indicates where in a full body message a partial message belongs.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Content-Range",
    },
    {
        "section": "Security",
        "name": "Cross-Origin-Embedder-Policy",
        "description": "Allows a server to declare an embedder policy for a given document.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Cross-Origin-Embedder-Policy",
    },
    {
        "section": "Security",
        "name": "Cross-Origin-Opener-Policy",
        "description": "Prevents other domains from opening/controlling a window.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Cross-Origin-Opener-Policy",
    },
    {
        "section": "Security",
        "name": "Cross-Origin-Resource-Policy",
        "description": "Prevents other domains from reading the response of the resources to which this header is applied. See also CORP explainer article.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Cross-Origin-Resource-Policy",
    },
    {
        "section": "Security",
        "name": "Content-Security-Policy",
        "description": "Controls resources the user agent is allowed to load for a given page.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Content-Security-Policy",
    },
    {
        "section": "Security",
        "name": "Content-Security-Policy-Report-Only",
        "description": "Allows web developers to experiment with policies by monitoring, but not enforcing, their effects. These violation reports consist of JSON documents sent via an HTTP POST request to the specified URI.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Content-Security-Policy-Report-Only",
    },
    {
        "section": "Security",
        "name": "Permissions-Policy",
        "description": "Provides a mechanism to allow and deny the use of browser features in a website's own frame, and in <iframe>s that it embeds.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Permissions-Policy",
    },
    {
        "section": "Security",
        "name": "Strict-Transport-Security",
        "description": "Force communication using HTTPS instead of HTTP.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security",
    },
    {
        "section": "Security",
        "name": "Upgrade-Insecure-Requests",
        "description": "Sends a signal to the server expressing the client's preference for an encrypted and authenticated response, and that it can successfully handle the upgrade-insecure-requests directive.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Upgrade-Insecure-Requests",
    },
    {
        "section": "Security",
        "name": "X-Content-Type-Options",
        "description": "Disables MIME sniffing and forces browser to use the type given in Content-Type.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options",
    },
    {
        "section": "Security",
        "name": "X-Frame-Options",
        "description": "Indicates whether a browser should be allowed to render a page in a <frame>, <iframe>, <embed> or <object>.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/X-Frame-Options",
    },
    {
        "section": "Security",
        "name": "X-XSS-Protection",
        "description": "Enables cross-site scripting filtering.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/X-XSS-Protection",
    },
    {
        "section": "Server-sent events",
        "name": "NEL",
        "description": "Defines a mechanism that enables developers to declare a network error reporting policy.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/NEL",
    },
    {
        "section": "Transfer coding",
        "name": "Transfer-Encoding",
        "description": "Specifies the form of encoding used to safely transfer the resource to the user.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Transfer-Encoding",
    },
    {
        "section": "Transfer coding",
        "name": "TE",
        "description": "Specifies the transfer encodings the user agent is willing to accept.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/TE",
    },
    {
        "section": "Transfer coding",
        "name": "Trailer",
        "description": "Allows the sender to include additional fields at the end of chunked message.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Trailer",
    },
    {
        "section": "Other",
        "name": "Alt-Svc",
        "description": "Used to list alternate ways to reach this service.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Alt-Svc",
    },
    {
        "section": "Other",
        "name": "Alt-Used",
        "description": "Used to identify the alternative service in use.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Alt-Used",
    },
    {
        "section": "Other",
        "name": "Date",
        "description": "Contains the date and time at which the message was originated.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Date",
    },
    {
        "section": "Other",
        "name": "Link",
        "description": "This entity-header field provides a means for serializing one or more links in HTTP headers. It is semantically equivalent to the HTML <link> element.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Link",
    },
    {
        "section": "Other",
        "name": "Retry-After",
        "description": "Indicates how long the user agent should wait before making a follow-up request.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Retry-After",
    },
    {
        "section": "Other",
        "name": "Server-Timing",
        "description": "Communicates one or more metrics and descriptions for the given request-response cycle.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Server-Timing",
    },
    {
        "section": "Other",
        "name": "SourceMap",
        "description": "Links generated code to a source map.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/SourceMap",
    },
    {
        "section": "Other",
        "name": "Upgrade",
        "description": "This HTTP/1.1 (only) header can be used to upgrade an already established client/server connection to a different protocol (over the same transport protocol). For example, it can be used by a client to upgrade a connection from HTTP 1.1 to HTTP 2.0, or an HTTP or HTTPS connection into a WebSocket.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Upgrade",
    },
    {
        "section": "Experimental",
        "name": "Speculation-Rules",
        "description": "Provides a list of URLs pointing to text resources containing speculation rule JSON definitions. When the response is an HTML document, these rules will be added to the document's speculation rule set.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/Speculation-Rules",
    },
    {
        "section": "Experimental",
        "name": "Supports-Loading-Mode",
        "description": "Set by a navigation target to opt-in to using various higher-risk loading modes. For example, cross-origin, same-site prerendering requires a Supports-Loading-Mode value of credentialed-prerender.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/Supports-Loading-Mode",
    },
    {
        "section": "Non-standard headers",
        "name": "X-Forwarded-For",
        "description": "Identifies the originating IP addresses of a client connecting to a web server through an HTTP proxy or a load balancer.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/X-Forwarded-For",
    },
    {
        "section": "Non-standard headers",
        "name": "X-Forwarded-Host",
        "description": "Identifies the original host requested that a client used to connect to your proxy or load balancer.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/X-Forwarded-Host",
    },
    {
        "section": "Non-standard headers",
        "name": "X-Forwarded-Proto",
        "description": "Identifies the protocol (HTTP or HTTPS) that a client used to connect to your proxy or load balancer.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/X-Forwarded-Proto",
    },
    {
        "section": "Non-standard headers",
        "name": "X-DNS-Prefetch-Control",
        "description": "Controls DNS prefetching, a feature by which browsers proactively perform domain name resolution on both links that the user may choose to follow as well as URLs for items referenced by the document, including images, CSS, JavaScript, and so forth.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/X-DNS-Prefetch-Control",
    },
    {
        "section": "Deprecated headers",
        "name": "Pragma",
        "description": "Implementation-specific header that may have various effects anywhere along the request-response chain. Used for backwards compatibility with HTTP/1.0 caches where the Cache-Control header is not yet present.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Pragma",
    },
    {
        "section": "Deprecated headers",
        "name": "Warning",
        "description": "General warning information about possible problems.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Warning",
    },
    {
        "section": "Redirects",
        "name": "Refresh",
        "description": 'Directs the browser to reload the page or redirect to another. Takes the same value as the meta element with http-equiv="refresh".',
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Refresh",
    },
    {
        "section": "Security",
        "name": "X-Permitted-Cross-Domain-Policies",
        "description": "Specifies if a cross-domain policy file (crossdomain.xml) is allowed. The file may define a policy to grant clients, such as Adobe's Flash Player (now obsolete), Adobe Acrobat, Microsoft Silverlight (now obsolete), or Apache Flex, permission to handle data across domains that would otherwise be restricted due to the Same-Origin Policy. See the Cross-domain Policy File Specification for more information.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/X-Permitted-Cross-Domain-Policies",
    },
    {
        "section": "Security",
        "name": "X-Powered-By",
        "description": "May be set by hosting environments or other frameworks and contains information about them while not providing any usefulness to the application or its visitors. Unset this header to avoid exposing potential vulnerabilities.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/X-Powered-By",
    },
    {
        "section": "Server-sent events",
        "name": "Report-To",
        "description": "Used to specify a server endpoint for the browser to send warning and error reports to.",
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/Report-To",
    },
    {
        "section": "Experimental headers",
        "name": "Origin-Isolation",
        "description": "Provides a mechanism to allow web applications to isolate their origins.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/Origin-Isolation",
    },
    {
        "section": "Experimental headers",
        "name": "Accept-Push-Policy",
        "description": "A client can express the desired push policy for a request by sending an Accept-Push-Policy header field in the request.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/Accept-Push-Policy",
    },
    {
        "section": "Experimental headers",
        "name": "Accept-Signature",
        "description": "A client can send the Accept-Signature header field to indicate intention to take advantage of any available signatures and to indicate what kinds of signatures it supports.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/Accept-Signature",
    },
    {
        "section": "Experimental headers",
        "name": "Early-Data",
        "description": "Indicates that the request has been conveyed in TLS early data.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/Early-Data",
    },
    {
        "section": "Experimental headers",
        "name": "Push-Policy",
        "description": "A Push-Policy defines the server behavior regarding push when processing a request.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/Push-Policy",
    },
    {
        "section": "Experimental headers",
        "name": "Signature",
        "description": "The Signature header field conveys a list of signatures for an exchange, each one accompanied by information about how to determine the authority of and refresh that signature.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/Signature",
    },
    {
        "section": "Experimental headers",
        "name": "Signed-Headers",
        "description": "The Signed-Headers header field identifies an ordered list of response header fields to include in a signature.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/Signed-Headers",
    },
    {
        "section": "Privacy",
        "name": "Sec-GPC",
        "description": "Indicates whether the user consents to a website or service selling or sharing their personal information with third parties.",
        "experimental": True,
        "url": "/en-US/docs/Web/HTTP/Headers/Sec-GPC",
    },
    {
        "section": "Non-standard headers",
        "name": "X-Robots-Tag",
        "description": 'The X-Robots-Tag HTTP header is used to indicate how a web page is to be indexed within public search engine results. The header is effectively equivalent to <meta name="robots" content="…">.',
        "experimental": False,
        "url": "/en-US/docs/Web/HTTP/Headers/X-Robots-Tag",
    },
]


request_header_names = {
    "Authorization",
    "Proxy-Authorization",
    "Cache-Control",
    "Clear-Site-Data",
    "If-Match",
    "If-None-Match",
    "If-Modified-Since",
    "If-Unmodified-Since",
    "Connection",
    "Keep-Alive",
    "Accept",
    "Accept-Encoding",
    "Accept-Language",
    "Expect",
    "Max-Forwards",
    "Cookie",
    "Access-Control-Request-Headers",
    "Access-Control-Request-Method",
    "Origin",
    "Timing-Allow-Origin",
    "Content-Length",
    "Content-Type",
    "Content-Encoding",
    "Content-Language",
    "Content-Location",
    "Forwarded",
    "Via",
    "From",
    "Host",
    "Referer",
    "Referrer-Policy",
    "User-Agent",
    "Range",
    "If-Range",
    "Upgrade-Insecure-Requests",
    "Transfer-Encoding",
    "TE",
    "Trailer",
    "Alt-Used",
    "Link",
    "Date",
    "Origin-Isolation",
    "Accept-Push-Policy",
    "Accept-Signature",
    "Early-Data",
    "Signature",
    "Signed-Headers",
    "Sec-GPC",
    "X-Forwarded-For",
    "X-Forwarded-Host",
    "X-Forwarded-Proto",
    "X-DNS-Prefetch-Control",
    "Pragma",
    "Warning",
}

REQUEST_HEADERS = [
    header for header in headers if header["name"] in request_header_names
]
