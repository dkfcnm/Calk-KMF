const DEFAULT_TTL = 60 * 60 * 1000; // 1 hour

export function getCached(key, ttl = DEFAULT_TTL) {
    try {
        const raw = localStorage.getItem(key);
        if (!raw) return null;
        const { data, timestamp } = JSON.parse(raw);
        if (Date.now() - timestamp > ttl) {
            localStorage.removeItem(key);
            return null;
        }
        return data;
    } catch {
        return null;
    }
}

export function setCached(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify({ data, timestamp: Date.now() }));
    } catch {
        // ignore
    }
}

export async function fetchCached(key, fetcher, ttl = DEFAULT_TTL) {
    const cached = getCached(key, ttl);
    if (cached) return cached;
    const data = await fetcher();
    setCached(key, data);
    return data;
}
