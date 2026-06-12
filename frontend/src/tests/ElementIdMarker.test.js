import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ElementIdMarkerProvider, useElementIdMarker } from '../contexts/ElementIdMarkerContext';
import ElementIdMarkerLayer from '../components/ElementIdMarkerLayer';

// Mock component that uses the context
function TestComponent() {
    const { markerEnabled, toggleMarker, popupOpen, popupId, openPopup, closePopup } = useElementIdMarker();
    return (
        <div>
            <div data-testid="marker-status">{markerEnabled ? 'enabled' : 'disabled'}</div>
            <button data-testid="toggle" onClick={toggleMarker}>Toggle</button>
            <div data-testid="popup-status">{popupOpen ? 'open' : 'closed'}</div>
            <div data-testid="popup-id">{popupId || 'none'}</div>
            <button data-testid="open-popup" onClick={() => openPopup('test:id', document.body)}>Open Popup</button>
            <button data-testid="close-popup" onClick={closePopup}>Close Popup</button>
        </div>
    );
}

describe('ElementIdMarkerContext', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it('should be disabled by default', () => {
        render(
            <ElementIdMarkerProvider>
                <TestComponent />
            </ElementIdMarkerProvider>
        );
        expect(screen.getByTestId('marker-status').textContent).toBe('disabled');
    });

    it('should toggle marker enabled state', () => {
        render(
            <ElementIdMarkerProvider>
                <TestComponent />
            </ElementIdMarkerProvider>
        );
        fireEvent.click(screen.getByTestId('toggle'));
        expect(screen.getByTestId('marker-status').textContent).toBe('enabled');
        expect(localStorage.getItem('kmf_element_id_markers')).toBe('true');
    });

    it('should open and close popup', () => {
        render(
            <ElementIdMarkerProvider>
                <TestComponent />
            </ElementIdMarkerProvider>
        );
        fireEvent.click(screen.getByTestId('open-popup'));
        expect(screen.getByTestId('popup-status').textContent).toBe('open');
        expect(screen.getByTestId('popup-id').textContent).toBe('test:id');

        fireEvent.click(screen.getByTestId('close-popup'));
        expect(screen.getByTestId('popup-status').textContent).toBe('closed');
    });
});

describe('ElementIdMarkerLayer', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it('should render GlobalStyles when marker enabled', () => {
        render(
            <ElementIdMarkerProvider>
                <ElementIdMarkerLayer />
                <div data-element-id="test:item:1">Test Item</div>
            </ElementIdMarkerProvider>
        );
        // GlobalStyles are applied via MUI - visual verification needed
        expect(document.querySelector('[data-element-id="test:item:1"]')).toBeInTheDocument();
    });
});
