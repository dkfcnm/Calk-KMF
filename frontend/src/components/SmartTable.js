import React, { useState, useEffect, useCallback, useMemo } from 'react';
import ElementIdBadge from './ElementIdBadge';
import { generateId } from '../hooks/useElementId';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Chip,
  IconButton,
  ToggleButtonGroup,
  ToggleButton,
  Menu,
  MenuItem,
  Checkbox,
  InputAdornment,
  Select,
  FormControl,
  InputLabel,
  Typography,
} from '@mui/material';
import {
  Save as SaveIcon,
  Cancel as CancelIcon,
  Edit as EditIcon,
  Settings as SettingsIcon,
  Search as SearchIcon,
  TextFields as TextFieldsIcon,
  Image as ImageIcon,
  VerticalSplit as VerticalSplitIcon,
} from '@mui/icons-material';

function SvgRenderer({ svgString, color, size = 24 }) {
  if (!svgString || !svgString.trim().startsWith('<svg')) return null;
  return (
    <Box
      component="span"
      sx={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: color || 'inherit',
        width: size,
        height: size,
        flexShrink: 0,
        '& svg': { width: size, height: size, display: 'block' },
      }}
      dangerouslySetInnerHTML={{ __html: svgString }}
    />
  );
}

function SmartTable({
  columns,
  data,
  idField,
  onSaveRow,
  storageKey,
  categoryFilter,
  displayMode,
  onDisplayModeChange,
  area: areaProp,
}) {
  const area = areaProp || storageKey || 'table';
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const [focusField, setFocusField] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [anchorEl, setAnchorEl] = useState(null);
  const [visibleColumns, setVisibleColumns] = useState(() => {
    try {
      const saved = localStorage.getItem(`refs_columns_${storageKey}`);
      if (saved) return JSON.parse(saved);
    } catch {}
    return columns.filter(c => c.defaultVisible !== false).map(c => c.key);
  });

  useEffect(() => {
    try {
      localStorage.setItem(`refs_columns_${storageKey}`, JSON.stringify(visibleColumns));
    } catch {}
  }, [visibleColumns, storageKey]);

  const startEdit = useCallback((item, fieldKey) => {
    const id = item[idField];
    setEditingId(id);
    setEditData({ ...item });
    setFocusField(fieldKey || null);
  }, [idField]);

  const cancelEdit = useCallback(() => {
    setEditingId(null);
    setEditData({});
    setFocusField(null);
  }, []);

  const handleChange = useCallback((field, value) => {
    setEditData(prev => ({ ...prev, [field]: value }));
  }, []);

  const saveEdit = useCallback(async () => {
    try {
      await onSaveRow(editData[idField], editData);
      setEditingId(null);
      setEditData({});
      setFocusField(null);
    } catch (err) {
      console.error(err);
    }
  }, [editData, idField, onSaveRow]);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      saveEdit();
    } else if (e.key === 'Escape') {
      cancelEdit();
    }
  }, [saveEdit, cancelEdit]);

  const filteredData = useMemo(() => {
    let result = [...data];
    if (activeCategory !== 'all' && categoryFilter) {
      result = result.filter(row => {
        if (categoryFilter.mapValue) {
          return categoryFilter.mapValue(row) === activeCategory;
        }
        return row[categoryFilter.key] === activeCategory;
      });
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(row => {
        return columns.some(col => {
          if (col.searchable === false) return false;
          if (col.type === 'chip' || col.type === 'text' || col.type === 'select' || col.type === 'multiline' || col.type === 'number' || !col.type) {
            const val = row[col.key];
            if (val == null) return false;
            return String(val).toLowerCase().includes(q);
          }
          return false;
        });
      });
    }
    return result;
  }, [data, activeCategory, categoryFilter, searchQuery, columns]);

  const isColumnVisible = (key) => visibleColumns.includes(key);

  const toggleColumn = (key) => {
    setVisibleColumns(prev => {
      if (prev.includes(key)) return prev.filter(k => k !== key);
      return [...prev, key];
    });
  };

  const renderCell = (row, col) => {
    const isEditing = editingId === row[idField];
    const val = isEditing ? editData[col.key] : row[col.key];

    if (isEditing && col.editable !== false) {
      if (col.type === 'select' && col.options) {
        return (
          <FormControl size="small" fullWidth>
            <Select
              value={val || ''}
              onChange={(e) => handleChange(col.key, e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus={col.key === focusField}
            >
              {col.options.map(opt => (
                <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
        );
      }
      if (col.type === 'color') {
        return (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TextField
              size="small"
              type="color"
              value={val || '#000000'}
              onChange={(e) => handleChange(col.key, e.target.value)}
              sx={{ width: 50, minWidth: 50 }}
              onKeyDown={handleKeyDown}
            />
            <TextField
              size="small"
              value={val || ''}
              onChange={(e) => handleChange(col.key, e.target.value)}
              sx={{ width: 90 }}
              onKeyDown={handleKeyDown}
            />
          </Box>
        );
      }
      if (col.type === 'number') {
        return (
          <TextField
            size="small"
            type="number"
            value={val ?? ''}
            onChange={(e) => handleChange(col.key, e.target.value === '' ? null : parseFloat(e.target.value))}
            onKeyDown={handleKeyDown}
            autoFocus={col.key === focusField}
            fullWidth={col.fullWidth}
          />
        );
      }
      if (col.type === 'multiline') {
        return (
          <TextField
            size="small"
            fullWidth
            multiline
            rows={2}
            value={val || ''}
            onChange={(e) => handleChange(col.key, e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus={col.key === focusField}
          />
        );
      }
      return (
        <TextField
          size="small"
          value={val || ''}
          onChange={(e) => handleChange(col.key, e.target.value)}
          onKeyDown={handleKeyDown}
          autoFocus={col.key === focusField}
          fullWidth={col.fullWidth}
        />
      );
    }

    if (col.render) {
      return col.render(row);
    }

    if (displayMode !== 'text' && col.iconField && row[col.iconField]) {
      const color = col.colorField ? row[col.colorField] : undefined;
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SvgRenderer svgString={row[col.iconField]} color={color} />
          {displayMode === 'both' && (
            <Typography variant="body2" noWrap>{val}</Typography>
          )}
        </Box>
      );
    }

    if (col.type === 'chip' || col.type === 'select') {
      const opt = col.options?.find(o => o.value === val);
      const label = opt ? opt.label : val;
      return <Chip label={label || '—'} size="small" variant="outlined" />;
    }

    if (col.type === 'color') {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 24, height: 24, bgcolor: val || '#ccc', borderRadius: 1, border: '1px solid #ddd', flexShrink: 0 }} />
          <Typography variant="body2" noWrap>{val}</Typography>
        </Box>
      );
    }

    if (col.type === 'multiline') {
      return (
        <Typography variant="body2" sx={{ maxWidth: col.maxWidth || 400, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {val}
        </Typography>
      );
    }

    return (
      <Typography
        variant="body2"
        sx={{
          color: col.colorField ? row[col.colorField] : 'inherit',
          fontWeight: col.bold ? 'bold' : 'normal',
          whiteSpace: col.wrap ? 'normal' : 'nowrap',
        }}
      >
        {val}
      </Typography>
    );
  };

  const visibleCols = columns.filter(c => isColumnVisible(c.key));

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <TextField
          size="small"
          placeholder="Поиск..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
          }}
          inputProps={{ 'data-element-id': generateId(area, 'search', 'query') }}
          sx={{ minWidth: 240 }}
        />
        {categoryFilter && (
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel>Фильтр</InputLabel>
            <Select
              value={activeCategory}
              label="Фильтр"
              onChange={(e) => setActiveCategory(e.target.value)}
              inputProps={{ 'data-element-id': generateId(area, 'filter', 'category') }}
            >
              <MenuItem value="all">Все</MenuItem>
              {categoryFilter.options.map(opt => (
                <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
        <Box sx={{ flexGrow: 1 }} />
        <ToggleButtonGroup
          value={displayMode}
          exclusive
          onChange={(e, val) => val && onDisplayModeChange(val)}
          size="small"
        >
          <ToggleButton value="text" title="Текст">
            <ElementIdBadge area={area} element="display" index="text">
              <TextFieldsIcon fontSize="small" />
            </ElementIdBadge>
          </ToggleButton>
          <ToggleButton value="icon" title="Иконки">
            <ElementIdBadge area={area} element="display" index="icon">
              <ImageIcon fontSize="small" />
            </ElementIdBadge>
          </ToggleButton>
          <ToggleButton value="both" title="И то и другое">
            <ElementIdBadge area={area} element="display" index="both">
              <VerticalSplitIcon fontSize="small" />
            </ElementIdBadge>
          </ToggleButton>
        </ToggleButtonGroup>
        <IconButton size="small" onClick={(e) => setAnchorEl(e.currentTarget)} title="Колонки">
          <ElementIdBadge area={area} element="settings" index="columns">
            <SettingsIcon fontSize="small" />
          </ElementIdBadge>
        </IconButton>
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
        >
          {columns.map(col => (
            <MenuItem key={col.key} onClick={() => toggleColumn(col.key)} dense>
              <Checkbox checked={isColumnVisible(col.key)} size="small" />
              <Typography variant="body2">{col.label}</Typography>
            </MenuItem>
          ))}
        </Menu>
      </Box>

      <TableContainer component={Paper} sx={{ width: '100%' }}>
        <Table size="small" sx={{ width: '100%' }}>
          <TableHead>
            <TableRow data-element-id={generateId(area, 'header', 'row')}>
              {visibleCols.map(col => (
                <TableCell key={col.key} sx={{ fontWeight: 'bold', whiteSpace: 'nowrap' }} data-element-id={generateId(area, 'header', col.key)}>
                  {col.label}
                </TableCell>
              ))}
              <TableCell sx={{ fontWeight: 'bold', whiteSpace: 'nowrap', width: 80 }} data-element-id={generateId(area, 'header', 'actions')}>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredData.map((row, rowIndex) => {
              const isEditing = editingId === row[idField];
              return (
                <TableRow key={row[idField]} hover data-element-id={generateId(area, 'row', rowIndex)}>
                  {visibleCols.map(col => (
                    <TableCell
                      key={col.key}
                      onClick={() => {
                        if (!isEditing && col.editable !== false) {
                          startEdit(row, col.key);
                        }
                      }}
                      sx={{
                        cursor: col.editable !== false ? 'pointer' : 'default',
                        maxWidth: col.maxWidth,
                      }}
                      data-element-id={generateId(area, 'cell', `${rowIndex}_${col.key}`)}
                    >
                      {renderCell(row, col)}
                    </TableCell>
                  ))}
                  <TableCell sx={{ whiteSpace: 'nowrap' }} data-element-id={generateId(area, 'actions', rowIndex)}>
                    {isEditing ? (
                      <Box sx={{ display: 'flex' }}>
                        <IconButton size="small" color="primary" onClick={saveEdit}>
                          <ElementIdBadge area={area} element="action" index={`save_${rowIndex}`}>
                            <SaveIcon fontSize="small" />
                          </ElementIdBadge>
                        </IconButton>
                        <IconButton size="small" onClick={cancelEdit}>
                          <ElementIdBadge area={area} element="action" index={`cancel_${rowIndex}`}>
                            <CancelIcon fontSize="small" />
                          </ElementIdBadge>
                        </IconButton>
                      </Box>
                    ) : (
                      <IconButton size="small" onClick={() => startEdit(row)}>
                        <ElementIdBadge area={area} element="action" index={`edit_${rowIndex}`}>
                          <EditIcon fontSize="small" />
                        </ElementIdBadge>
                      </IconButton>
                    )}
                  </TableCell>
                </TableRow>
              );
            })}
            {filteredData.length === 0 && (
              <TableRow data-element-id={generateId(area, 'row', 'empty')}>
                <TableCell colSpan={visibleCols.length + 1} align="center" data-element-id={generateId(area, 'cell', 'empty')}>
                  <Typography variant="body2" color="text.secondary">Нет данных</Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default React.memo(SmartTable);
