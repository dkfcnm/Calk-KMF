import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';
import { createTheme } from '@mui/material/styles';

const STORAGE_KEY = 'kmf_display_settings';

const defaultSettings = {
    theme: 'light',
    density: 'comfortable',
    language: 'ru',
};

function loadSettings() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) return { ...defaultSettings, ...JSON.parse(saved) };
    } catch {}
    return { ...defaultSettings };
}

function saveSettings(settings) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    } catch {}
}

const DisplaySettingsContext = createContext({
    settings: defaultSettings,
    setTheme: () => {},
    setDensity: () => {},
    setLanguage: () => {},
    theme: createTheme({ palette: { mode: 'light' } }),
});

export function DisplaySettingsProvider({ children }) {
    const [settings, setSettings] = useState(loadSettings);

    const updateSettings = useCallback((partial) => {
        setSettings(prev => {
            const next = { ...prev, ...partial };
            saveSettings(next);
            return next;
        });
    }, []);

    const setTheme = useCallback((theme) => updateSettings({ theme }), [updateSettings]);
    const setDensity = useCallback((density) => updateSettings({ density }), [updateSettings]);
    const setLanguage = useCallback((language) => updateSettings({ language }), [updateSettings]);

    const muiTheme = useMemo(() => {
        const isDark = settings.theme === 'dark';
        return createTheme({
            palette: {
                mode: isDark ? 'dark' : 'light',
                primary: { main: '#673ab7' },
                secondary: { main: '#ff9800' },
            },
        });
    }, [settings.theme]);

    const contextValue = useMemo(() => ({
        settings, setTheme, setDensity, setLanguage, theme: muiTheme
    }), [settings, setTheme, setDensity, setLanguage, muiTheme]);

    return (
        <DisplaySettingsContext.Provider value={contextValue}>
            {children}
        </DisplaySettingsContext.Provider>
    );
}

export function useDisplaySettings() {
    return useContext(DisplaySettingsContext);
}
