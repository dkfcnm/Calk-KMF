import React from 'react';
import { GlobalStyles, Popover, Box, Typography, Fade } from '@mui/material';
import { useElementIdMarker } from '../contexts/ElementIdMarkerContext';

const markerStyles = {
    '[data-element-id]': {
        position: 'relative !important',
    },
    '[data-element-id]::after': {
        content: '"\\00A1"',
        position: 'absolute',
        top: '2px',
        right: '2px',
        color: '#777',
        fontSize: '14px',
        fontWeight: 'bold',
        lineHeight: 1,
        pointerEvents: 'none',
        zIndex: 9999,
        fontFamily: 'monospace',
        backgroundColor: 'rgba(255, 255, 255, 0.85)',
        borderRadius: '3px',
        padding: '1px 3px',
        boxShadow: '0 0 2px rgba(0,0,0,0.1)',
    },
    '[data-element-id]:hover::after': {
        color: '#333',
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        boxShadow: '0 0 4px rgba(0,0,0,0.2)',
    },
};

export default function ElementIdMarkerLayer() {
    const {
        markerEnabled,
        popupOpen,
        popupId,
        popupAnchor,
        closePopup,
        copyId,
    } = useElementIdMarker();

    const handleCopy = () => {
        copyId(popupId);
        closePopup();
    };

    return (
        <>
            {markerEnabled && <GlobalStyles styles={markerStyles} />}
            <Popover
                open={popupOpen}
                anchorEl={popupAnchor}
                onClose={closePopup}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                TransitionComponent={Fade}
                slotProps={{
                    paper: {
                        sx: {
                            p: 2,
                            minWidth: 200,
                            maxWidth: 320,
                            wordBreak: 'break-all',
                        },
                    },
                }}
            >
                <Box>
                    <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                        ID элемента
                    </Typography>
                    <Typography
                        variant="body2"
                        sx={{
                            fontFamily: 'monospace',
                            cursor: 'pointer',
                            bgcolor: 'grey.100',
                            p: 1,
                            borderRadius: 1,
                            '&:hover': {
                                bgcolor: 'primary.light',
                                color: 'primary.contrastText',
                            },
                        }}
                        onClick={handleCopy}
                        title="Кликните для копирования"
                    >
                        {popupId}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                        (кликните на ID для копирования)
                    </Typography>
                </Box>
            </Popover>
        </>
    );
}
