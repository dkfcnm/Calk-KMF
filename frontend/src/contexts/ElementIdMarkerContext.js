import React, { createContext, useContext, useState, useCallback, useEffect, useMemo } from 'react';

const STORAGE_KEY = 'kmf_element_id_markers';

const ElementIdMarkerContext = createContext({
    markerEnabled: false,
    toggleMarker: () => {},
    popupOpen: false,
    popupId: null,
    popupAnchor: null,
    openPopup: () => {},
    closePopup: () => {},
    copyId: () => {},
});

export function ElementIdMarkerProvider({ children }) {
    const [markerEnabled, setMarkerEnabled] = useState(() => {
        try {
            return localStorage.getItem(STORAGE_KEY) === 'true';
        } catch {
            return false;
        }
    });

    const [popupOpen, setPopupOpen] = useState(false);
    const [popupId, setPopupId] = useState(null);
    const [popupAnchor, setPopupAnchor] = useState(null);

    const toggleMarker = useCallback(() => {
        setMarkerEnabled(prev => {
            const next = !prev;
            try {
                localStorage.setItem(STORAGE_KEY, next ? 'true' : 'false');
            } catch {}
            return next;
        });
    }, []);

    const openPopup = useCallback((id, anchorEl) => {
        setPopupId(id);
        setPopupAnchor(anchorEl);
        setPopupOpen(true);
    }, []);

    const closePopup = useCallback(() => {
        setPopupOpen(false);
        setPopupId(null);
        setPopupAnchor(null);
    }, []);

    const copyId = useCallback((id) => {
        if (navigator.clipboard && id) {
            navigator.clipboard.writeText(id).catch(() => {});
        }
    }, []);

    // Global click handler for ¡ markers
    useEffect(() => {
        if (!markerEnabled) return;

        const handleClick = (e) => {
            const el = e.target.closest('[data-element-id]');
            if (!el) return;

            const rect = el.getBoundingClientRect();
            const markerSize = 22;
            const inMarkerZone = (
                e.clientX >= rect.right - markerSize &&
                e.clientY <= rect.top + markerSize
            );

            if (inMarkerZone) {
                e.stopPropagation();
                e.preventDefault();
                const id = el.getAttribute('data-element-id');
                openPopup(id, el);
            }
        };

        document.addEventListener('click', handleClick, true);
        return () => document.removeEventListener('click', handleClick, true);
    }, [markerEnabled, openPopup]);

    return (
        <ElementIdMarkerContext.Provider
            value={useMemo(() => ({
                markerEnabled, toggleMarker, popupOpen, popupId, popupAnchor, openPopup, closePopup, copyId,
            }), [markerEnabled, toggleMarker, popupOpen, popupId, popupAnchor, openPopup, closePopup, copyId])}
        >
            {children}
        </ElementIdMarkerContext.Provider>
    );
}

export function useElementIdMarker() {
    return useContext(ElementIdMarkerContext);
}
