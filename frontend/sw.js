/**
 * Service Worker for Sahaaya PWA
 * Provides offline functionality and caching strategies
 */

const CACHE_NAME = "sahaaya-v1.2.0";
const API_CACHE_NAME = "sahaaya-api-v1.2.0";

// Files to cache for offline functionality
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/styles.css",
  "/app.js",
  "/voice-handler.js",
  "/connectivity.js",
  "/translations.js",
  "/manifest.json",

  // Fonts
  "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
  "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",

  // Icons (when available)
  "/icons/icon-192x192.png",
  "/icons/icon-512x512.png",
];

// API endpoints that can be cached
const CACHEABLE_API_ENDPOINTS = [
  "/connectivity-status",
  "/offline-guidance",
  "/emergency-protocol",
];

// Install event - cache static assets
self.addEventListener("install", (event) => {
  console.log("Sahaaya SW: Installing service worker");

  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => {
        console.log("Sahaaya SW: Caching static assets");
        return cache.addAll(
          STATIC_ASSETS.filter((asset) => !asset.startsWith("http"))
        );
      })
      .then(() => {
        console.log("Sahaaya SW: Installation complete");
        self.skipWaiting();
      })
      .catch((error) => {
        console.error("Sahaaya SW: Installation failed", error);
      })
  );
});

// Activate event - cleanup old caches
self.addEventListener("activate", (event) => {
  console.log("Sahaaya SW: Activating service worker");

  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return (
                cacheName.startsWith("sahaaya-") &&
                cacheName !== CACHE_NAME &&
                cacheName !== API_CACHE_NAME
              );
            })
            .map((cacheName) => {
              console.log("Sahaaya SW: Deleting old cache", cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        console.log("Sahaaya SW: Activation complete");
        return self.clients.claim();
      })
  );
});

// Fetch event - implement caching strategies
self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== "GET") {
    return;
  }

  // Handle different types of requests
  if (isAPIRequest(url)) {
    event.respondWith(handleAPIRequest(request));
  } else if (isStaticAsset(url)) {
    event.respondWith(handleStaticAsset(request));
  } else if (isNavigationRequest(request)) {
    event.respondWith(handleNavigationRequest(request));
  } else {
    event.respondWith(handleOtherRequests(request));
  }
});

// Check if request is for API
function isAPIRequest(url) {
  return (
    url.pathname.startsWith("/api/") ||
    CACHEABLE_API_ENDPOINTS.some((endpoint) =>
      url.pathname.startsWith(endpoint)
    ) ||
    url.pathname.match(
      /^\/(smart-process|offline-guidance|emergency-protocol|connectivity-status)$/
    )
  );
}

// Check if request is for static asset
function isStaticAsset(url) {
  return (
    url.pathname.match(
      /\.(css|js|png|jpg|jpeg|svg|ico|woff|woff2|ttf|json)$/
    ) || STATIC_ASSETS.includes(url.pathname)
  );
}

// Check if request is navigation
function isNavigationRequest(request) {
  return (
    request.mode === "navigate" ||
    (request.method === "GET" &&
      request.headers.get("accept").includes("text/html"))
  );
}

// Handle API requests - network first, cache fallback
async function handleAPIRequest(request) {
  const url = new URL(request.url);

  try {
    // Try network first
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      // Cache successful API responses
      const cache = await caches.open(API_CACHE_NAME);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }

    throw new Error(`API request failed: ${networkResponse.status}`);
  } catch (error) {
    console.log("Sahaaya SW: Network failed, trying cache for", url.pathname);

    // Try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Return offline fallback for specific endpoints
    return getOfflineFallback(url.pathname);
  }
}

// Handle static assets - cache first, network fallback
async function handleStaticAsset(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Not in cache, try network
    const networkResponse = await fetch(request);

    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    console.error("Sahaaya SW: Failed to load static asset", request.url);

    // Return offline placeholder if available
    if (request.url.includes("icon") || request.url.includes("image")) {
      return new Response("", { status: 404 });
    }

    throw error;
  }
}

// Handle navigation requests - cache first, network fallback
async function handleNavigationRequest(request) {
  try {
    const networkResponse = await fetch(request);
    return networkResponse;
  } catch (error) {
    console.log(
      "Sahaaya SW: Network failed for navigation, serving cached index.html"
    );

    const cachedResponse =
      (await caches.match("/index.html")) || (await caches.match("/"));

    if (cachedResponse) {
      return cachedResponse;
    }

    // Offline fallback page
    return new Response(
      `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Sahaaya - Offline</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 2rem; background: #f9fafb; }
                    .container { max-width: 400px; margin: 0 auto; background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    .icon { font-size: 4rem; margin-bottom: 1rem; }
                    h1 { color: #2563eb; margin-bottom: 1rem; }
                    p { color: #6b7280; line-height: 1.6; }
                    .retry-btn { background: #2563eb; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; cursor: pointer; margin-top: 1rem; }
                    .retry-btn:hover { background: #1d4ed8; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">🏥</div>
                    <h1>Sahaaya Health</h1>
                    <p>You're currently offline. Don't worry - Sahaaya can still provide basic health guidance using local data.</p>
                    <p>Connect to the internet for enhanced AI features.</p>
                    <button class="retry-btn" onclick="window.location.reload()">Try Again</button>
                </div>
            </body>
            </html>
        `,
      {
        headers: { "Content-Type": "text/html" },
      }
    );
  }
}

// Handle other requests
async function handleOtherRequests(request) {
  try {
    return await fetch(request);
  } catch (error) {
    console.log("Sahaaya SW: Request failed", request.url);
    throw error;
  }
}

// Get offline fallback response for specific API endpoints
function getOfflineFallback(pathname) {
  const fallbackResponses = {
    "/connectivity-status": {
      internet_available: false,
      recommended_mode: "offline",
      offline_capabilities: true,
      message: "Operating in offline mode",
    },

    "/offline-guidance": {
      guidance:
        "Offline mode active. Basic health guidance available. For serious symptoms, seek immediate medical attention.",
      processing_mode: "offline",
      emergency_contact: "108",
      message: "Limited offline functionality",
    },

    "/emergency-protocol": {
      emergency_guidance: {
        guidance:
          "Call emergency services immediately: 108 for medical emergencies, 100 for police.",
        emergency_contact: "108",
        immediate_action: "Seek immediate professional medical help",
      },
      emergency_contacts: [
        { name: "Emergency Medical", contact: "108", availability: "24/7" },
        { name: "Police", contact: "100", availability: "24/7" },
        { name: "Fire Service", contact: "101", availability: "24/7" },
      ],
      processing_mode: "offline_emergency",
    },

    "/smart-process": {
      guidance:
        "Currently offline. For medical emergencies, call 108 immediately. For non-urgent health concerns, please connect to the internet for detailed guidance.",
      processing_mode: "offline",
      offline_message: true,
      emergency_contact: "108",
    },
  };

  const fallback = fallbackResponses[pathname];

  if (fallback) {
    return new Response(JSON.stringify(fallback), {
      headers: { "Content-Type": "application/json" },
      status: 200,
    });
  }

  // Generic offline response
  return new Response(
    JSON.stringify({
      error: "Service unavailable offline",
      message: "This feature requires internet connectivity",
      offline_mode: true,
    }),
    {
      headers: { "Content-Type": "application/json" },
      status: 503,
    }
  );
}

// Background sync for failed requests
self.addEventListener("sync", (event) => {
  if (event.tag === "health-query-sync") {
    event.waitUntil(syncFailedQueries());
  }
});

// Sync failed queries when back online
async function syncFailedQueries() {
  try {
    const failedQueries = await getFailedQueries();

    for (const query of failedQueries) {
      try {
        const response = await fetch("/smart-process", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(query),
        });

        if (response.ok) {
          await removeFailedQuery(query.id);
          await notifyClient("Query synced successfully");
        }
      } catch (error) {
        console.log("Failed to sync query:", error);
      }
    }
  } catch (error) {
    console.error("Sync failed:", error);
  }
}

// Store failed query for later sync
async function storeFailedQuery(query) {
  const failedQueries = await getFailedQueries();
  failedQueries.push({
    ...query,
    id: Date.now(),
    timestamp: new Date().toISOString(),
  });

  await self.registration.sync.register("health-query-sync");
  return setFailedQueries(failedQueries);
}

// Get failed queries from IndexedDB (simplified implementation)
async function getFailedQueries() {
  // In a real implementation, use IndexedDB
  // For now, return empty array
  return [];
}

async function setFailedQueries(queries) {
  // In a real implementation, store in IndexedDB
  return Promise.resolve();
}

async function removeFailedQuery(id) {
  // In a real implementation, remove from IndexedDB
  return Promise.resolve();
}

// Notify clients about events
async function notifyClient(message) {
  const clients = await self.clients.matchAll();
  clients.forEach((client) => {
    client.postMessage({
      type: "SW_MESSAGE",
      message: message,
    });
  });
}

// Handle push notifications (for future use)
self.addEventListener("push", (event) => {
  if (event.data) {
    const data = event.data.json();

    const options = {
      body: data.body,
      icon: "/icons/icon-192x192.png",
      badge: "/icons/icon-96x96.png",
      tag: "sahaaya-notification",
      requireInteraction: data.urgent || false,
      actions: [
        {
          action: "open",
          title: "Open Sahaaya",
          icon: "/icons/icon-96x96.png",
        },
        {
          action: "dismiss",
          title: "Dismiss",
        },
      ],
    };

    event.waitUntil(
      self.registration.showNotification(
        data.title || "Sahaaya Health",
        options
      )
    );
  }
});

// Handle notification clicks
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  if (event.action === "open") {
    event.waitUntil(clients.openWindow("/"));
  }
});

console.log("Sahaaya SW: Service Worker loaded successfully");
