import { useCallback, useMemo } from 'react';

export function generateId(area, element, identifier) {
    const safeArea = String(area).toLowerCase().replace(/[^a-z0-9]/g, '_');
    const safeElement = String(element).toLowerCase().replace(/[^a-z0-9]/g, '_');
    const safeId = identifier !== undefined ? String(identifier).toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9_-]/g, '_') : '';
    return safeId ? `${safeArea}:${safeElement}:${safeId}` : `${safeArea}:${safeElement}`;
}

export function useElementId(area, element, identifier) {
    const id = useMemo(() => {
        const safeId = String(identifier ?? '').replace(/\s+/g, '-');
        return `${area}:${element}:${safeId}`;
    }, [area, element, identifier]);

    const copyToClipboard = useCallback(() => {
        navigator.clipboard.writeText(id).catch(() => {});
    }, [id]);

    return {
        id,
        dataId: { 'data-element-id': id },
        copyToClipboard,
    };
}
