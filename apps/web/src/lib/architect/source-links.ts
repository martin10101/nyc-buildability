/** Only observed official ZR article/chapter/section forms. No reconstructed link when the capture omits its URL. */
export function officialZoningTextUrl(value: unknown): string | null {
    if (typeof value !== "string" || !value.startsWith("https://zoningresolution.planning.nyc.gov/") || value.length > 500 || /[\u0000-\u0020\u007f\\]/.test(value))
        return null;
    try {
        const url = new URL(value);
        if (url.protocol !== "https:" || url.hostname !== "zoningresolution.planning.nyc.gov" || url.username || url.password || url.port || url.search)
            return null;
        if (!/^\/article-[ivxlcdm]+\/chapter-\d{1,2}(?:\/\d{2}-\d{2,4})?$/.test(url.pathname) || (url.hash && !/^#\d{2}-\d{2,4}$/.test(url.hash)))
            return null;
        return `https://zoningresolution.planning.nyc.gov${url.pathname}${url.hash}`;
    }
    catch {
        return null;
    }
}
