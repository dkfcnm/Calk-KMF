import React from 'react';
import { Tooltip, Box, Fade } from '@mui/material';
import { useDebugMode } from '../contexts/DebugModeContext';

export default function ElementIdBadge({ id, children, placement = 'top' }) {
    const { debugMode } = useDebugMode();

    const handleClick = (e) => {
        e.stopPropagation();
        navigator.clipboard.writeText(id).catch(() => {});
    };

    return (
        <Tooltip
            title={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <span>{id}</span>
                    <span style={{ fontSize: '0.75em', opacity: 0.7 }}>(клик — копировать)</span>
                </Box>
            }
            placement={placement}
            arrow
            TransitionComponent={Fade}
            enterDelay={300}
        >
            <Box
                component="span"
                onClick={handleClick}
                data-element-id={id}
                sx={{
                    position: 'relative',
                    display: 'inline-block',
                    cursor: debugMode ? 'crosshair' : 'inherit',
                    outline: debugMode ? '1px dashed rgba(103, 58, 183, 0.4)' : 'none',
                    '&:hover': {
                        outline: debugMode ? '2px solid rgba(103, 58, 183, 0.7)' : 'none',
                    },
                }}
            >
                {children}
                {debugMode && (
                    <Box
                        sx={{
                            position: 'absolute',
                            top: -2,
                            right: -2,
                            bgcolor: 'primary.main',
                            color: 'primary.contrastText',
                            fontSize: '9px',
                            px: 0.5,
                            py: 0.1,
                            borderRadius: 0.5,
                            zIndex: 9999,
                            pointerEvents: 'none',
                            whiteSpace: 'nowrap',
                            maxWidth: 120,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            lineHeight: 1.2,
                        }}
                    >
                        {id}
                    </Box>
                )}
            </Box>
        </Tooltip>
    );
}
