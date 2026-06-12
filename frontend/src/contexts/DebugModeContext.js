import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';

const DebugModeContext = createContext({
    debugMode: false,
    toggleDebugMode: () => {},
});

export function DebugModeProvider({ children }) {
    const [debugMode, setDebugMode] = useState(() => {
        try {
            return localStorage.getItem('kmf_debug_ids') === 'true';
        } catch {
            return false;
        }
    });

    const toggleDebugMode = useCallback(() => {
        setDebugMode(prev => {
            const next = !prev;
            try {
                localStorage.setItem('kmf_debug_ids', next ? 'true' : 'false');
            } catch {}
            return next;
        });
    }, []);

    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                toggleDebugMode();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [toggleDebugMode]);

    return (
        <DebugModeContext.Provider value={useMemo(() => ({ debugMode, toggleDebugMode }), [debugMode, toggleDebugMode])}>
            {children}
        </DebugModeContext.Provider>
    );
}

export function useDebugMode() {
    return useContext(DebugModeContext);
}
