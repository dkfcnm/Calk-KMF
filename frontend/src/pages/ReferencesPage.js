import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import SmartTable from '../components/SmartTable';
import refsService from '../services/refsService';
import qimenService from '../services/qimenService';
import { generateId } from '../hooks/useElementId';

const TABS = [
  { label: '12 ОФИЦЕРОВ', key: 'officers', storageKey: 'officers' },
  { label: '28 СОЗВЕЗДИЙ', key: 'constellations', storageKey: 'constellations' },
  { label: 'ЗВЁЗДЫ ПОЯСА', key: 'beltStars', storageKey: 'beltStars' },
  { label: '10 НС', key: 'stems', storageKey: 'stems' },
  { label: '12 ЗВ', key: 'branches', storageKey: 'branches' },
  { label: 'ЧЁРНЫЙ КРОЛИК', key: 'blackRabbit', storageKey: 'blackRabbit' },
  { label: 'ЭЛЕМЕНТЫ', key: 'elements', storageKey: 'elements' },
  { label: 'ШЕНЬ ША', key: 'shensha', storageKey: 'shensha' },
  { label: 'QM ЗВЁЗДЫ', key: 'qimenStars', storageKey: 'qimenStars' },
  { label: 'QM ВРАТА', key: 'qimenGates', storageKey: 'qimenGates' },
  { label: 'QM ДУХИ', key: 'qimenSpirits', storageKey: 'qimenSpirits' },
  { label: 'QM КОМБО', key: 'qimenCombos', storageKey: 'qimenCombos' },
  { label: 'QM ТРИГРАММЫ', key: 'qimenTrigrams', storageKey: 'qimenTrigrams' },
];

const CATEGORY_COLORS = {
  auspicious: 'success',
  mixed: 'warning',
  inauspicious: 'error',
};

const CATEGORY_LABELS_RU = {
  auspicious: 'Благоприятный',
  mixed: 'Смешанный',
  inauspicious: 'Неблагоприятный',
};

const DIRECTIONS_RU = {
  'East/Azure Dragon': 'Восток/Лазурный Дракон',
  'North/Black Tortoise': 'Север/Чёрная Черепаха',
  'West/White Tiger': 'Запад/Белый Тигр',
  'South/Vermillion Bird': 'Юг/Алый Птица',
};

const OFFICER_COLUMNS = [
  { key: 'officer_value_id', label: 'ID', editable: false },
  { key: 'officer_char', label: 'Символ', bold: true, iconField: 'icon_svg', colorField: 'color_hex' },
  { key: 'officer_pinyin', label: 'Пиньинь' },
  { key: 'officer_name_ru', label: 'Название (RU)' },
  { key: 'officer_name_en', label: 'Название (EN)' },
  {
    key: 'officer_category',
    label: 'Категория',
    type: 'select',
    options: [
      { value: 'auspicious', label: 'Благоприятный' },
      { value: 'mixed', label: 'Смешанный' },
      { value: 'inauspicious', label: 'Неблагоприятный' },
    ],
    render: (row) => row.officer_category ? (
      <Chip label={CATEGORY_LABELS_RU[row.officer_category] || row.officer_category} color={CATEGORY_COLORS[row.officer_category] || 'default'} size="small" />
    ) : null,
  },
  { key: 'description_ru', label: 'Описание', type: 'multiline', fullWidth: true },
  { key: 'description_short_ru', label: 'Краткое' },
];

const CONSTELLATION_COLUMNS = [
  { key: 'constellation_id', label: 'ID', editable: false },
  { key: 'constellation_char', label: 'Символ', bold: true, iconField: 'icon_svg', colorField: 'color_hex' },
  { key: 'constellation_pinyin', label: 'Пиньинь' },
  { key: 'constellation_name_ru', label: 'Название (RU)' },
  {
    key: 'direction_group',
    label: 'Направление',
    type: 'select',
    options: [
      { value: 'East/Azure Dragon', label: 'Восток/Лазурный Дракон' },
      { value: 'North/Black Tortoise', label: 'Север/Чёрная Черепаха' },
      { value: 'West/White Tiger', label: 'Запад/Белый Тигр' },
      { value: 'South/Vermillion Bird', label: 'Юг/Алый Птица' },
    ],
    render: (row) => DIRECTIONS_RU[row.direction_group] || row.direction_group,
  },
  { key: 'element', label: 'Элемент' },
  { key: 'animal_ru', label: 'Животное' },
  {
    key: 'nature',
    label: 'Характер',
    type: 'select',
    options: [
      { value: 'auspicious', label: 'Благоприятный' },
      { value: 'mixed', label: 'Смешанный' },
      { value: 'inauspicious', label: 'Неблагоприятный' },
    ],
    render: (row) => row.nature ? (
      <Chip label={CATEGORY_LABELS_RU[row.nature] || row.nature} color={CATEGORY_COLORS[row.nature] || 'default'} size="small" />
    ) : null,
  },
  { key: 'description_ru', label: 'Описание', type: 'multiline', fullWidth: true },
];

const BELT_COLUMNS = [
  { key: 'id', label: 'ID', editable: false },
  { key: 'name', label: 'Название' },
  { key: 'score', label: 'Счёт', type: 'number' },
  {
    key: 'type',
    label: 'Тип',
    editable: false,
    render: (row) => {
      const type = row.score > 0 ? 'yellow' : row.score < 0 ? 'black' : 'neutral';
      const label = type === 'yellow' ? 'Жёлтый' : type === 'black' ? 'Чёрный' : 'Нейтральный';
      const color = type === 'yellow' ? 'success' : type === 'black' ? 'error' : 'default';
      return <Chip label={label} color={color} size="small" />;
    },
  },
];

const STEM_COLUMNS = [
  { key: 'stem_id', label: 'ID', editable: false },
  { key: 'stem_char', label: 'Символ', bold: true, iconField: 'icon_svg', colorField: 'color_hex' },
  { key: 'stem_pinyin', label: 'Пиньинь' },
  { key: 'stem_rus', label: 'Название' },
  { key: 'element', label: 'Элемент' },
  { key: 'yin_yang', label: 'Инь/Ян' },
  { key: 'guigu_score', label: 'Счёт', type: 'number' },
  { key: 'color_hex', label: 'Цвет', type: 'color' },
];

const BRANCH_COLUMNS = [
  { key: 'branch_id', label: 'ID', editable: false },
  { key: 'branch_char', label: 'Символ', bold: true, iconField: 'icon_svg', colorField: 'color_hex' },
  { key: 'branch_pinyin', label: 'Пиньинь' },
  { key: 'branch_rus', label: 'Животное' },
  { key: 'element', label: 'Элемент' },
  { key: 'yin_yang', label: 'Инь/Ян' },
  { key: 'yuan_level', label: 'Юань', type: 'number' },
  { key: 'start_hour', label: 'Час нач', type: 'number' },
  { key: 'end_hour', label: 'Час кон', type: 'number' },
  { key: 'guigu_score', label: 'Счёт', type: 'number' },
  { key: 'color_hex', label: 'Цвет', type: 'color' },
];

const BLACK_RABBIT_COLUMNS = [
  { key: 'star_name', label: 'Название звезды', bold: true, iconField: 'icon_svg', colorField: 'color_hex', editable: false },
  { key: 'description_ru', label: 'Описание', type: 'multiline', fullWidth: true },
  {
    key: 'nature',
    label: 'Характер',
    type: 'select',
    options: [
      { value: 'auspicious', label: 'Благоприятный' },
      { value: 'mixed', label: 'Смешанный' },
      { value: 'inauspicious', label: 'Неблагоприятный' },
    ],
    render: (row) => row.nature ? (
      <Chip label={CATEGORY_LABELS_RU[row.nature] || row.nature} color={CATEGORY_COLORS[row.nature] || 'default'} size="small" />
    ) : '—',
  },
  { key: 'color_hex', label: 'Цвет', type: 'color' },
];

const ELEMENT_COLUMNS = [
  { key: 'element_id', label: 'ID', editable: false },
  { key: 'element_char', label: 'Символ', bold: true, iconField: 'icon_svg', colorField: 'color_hex' },
  { key: 'element_name_ru', label: 'Название (RU)' },
  { key: 'element_name_en', label: 'Название (EN)' },
  { key: 'color_hex', label: 'Цвет', type: 'color' },
  { key: 'bg_color_hex', label: 'Фон', type: 'color' },
  { key: 'text_color_hex', label: 'Текст', type: 'color' },
  { key: 'display_order', label: 'Порядок', type: 'number' },
];

const QIMEN_STAR_COLUMNS = [
  { key: 'star_id', label: 'ID', editable: false },
  { key: 'star_char', label: 'Символ', bold: true },
  { key: 'star_name_ru', label: 'Название' },
  { key: 'star_name_en', label: 'EN' },
  { key: 'palace_orig', label: 'Дворец', type: 'number' },
  { key: 'element', label: 'Элемент' },
  {
    key: 'nature',
    label: 'Характер',
    type: 'select',
    options: [
      { value: 'auspicious', label: 'Благоприятный' },
      { value: 'mixed', label: 'Смешанный' },
      { value: 'inauspicious', label: 'Неблагоприятный' },
    ],
    render: (row) => row.nature ? (
      <Chip label={CATEGORY_LABELS_RU[row.nature] || row.nature} color={CATEGORY_COLORS[row.nature] || 'default'} size="small" />
    ) : null,
  },
  { key: 'description_ru', label: 'Описание', type: 'multiline', fullWidth: true },
];

const QIMEN_GATE_COLUMNS = [
  { key: 'gate_id', label: 'ID', editable: false },
  { key: 'gate_char', label: 'Символ', bold: true },
  { key: 'gate_name_ru', label: 'Название' },
  { key: 'gate_name_en', label: 'EN' },
  { key: 'palace_orig', label: 'Дворец', type: 'number' },
  { key: 'element', label: 'Элемент' },
  {
    key: 'nature',
    label: 'Характер',
    type: 'select',
    options: [
      { value: 'auspicious', label: 'Благоприятный' },
      { value: 'mixed', label: 'Смешанный' },
      { value: 'inauspicious', label: 'Неблагоприятный' },
    ],
    render: (row) => row.nature ? (
      <Chip label={CATEGORY_LABELS_RU[row.nature] || row.nature} color={CATEGORY_COLORS[row.nature] || 'default'} size="small" />
    ) : null,
  },
  { key: 'description_ru', label: 'Описание', type: 'multiline', fullWidth: true },
];

const QIMEN_SPIRIT_COLUMNS = [
  { key: 'spirit_id', label: 'ID', editable: false },
  { key: 'spirit_char', label: 'Символ', bold: true },
  { key: 'spirit_name_ru', label: 'Название' },
  { key: 'spirit_name_en', label: 'EN' },
  { key: 'element', label: 'Элемент' },
  {
    key: 'nature',
    label: 'Характер',
    type: 'select',
    options: [
      { value: 'auspicious', label: 'Благоприятный' },
      { value: 'mixed', label: 'Смешанный' },
      { value: 'inauspicious', label: 'Неблагоприятный' },
    ],
    render: (row) => row.nature ? (
      <Chip label={CATEGORY_LABELS_RU[row.nature] || row.nature} color={CATEGORY_COLORS[row.nature] || 'default'} size="small" />
    ) : null,
  },
  { key: 'description_ru', label: 'Описание', type: 'multiline', fullWidth: true },
];

const QIMEN_COMBO_COLUMNS = [
  { key: 'combo_id', label: 'ID', editable: false },
  { key: 'combo_char', label: 'Комбинация', bold: true },
  { key: 'stem_top', label: 'Верх' },
  { key: 'stem_bottom', label: 'Низ' },
  {
    key: 'favorability',
    label: 'Благоприятность',
    type: 'number',
    render: (row) => {
      const color = row.favorability > 0 ? 'success' : row.favorability < 0 ? 'error' : 'warning';
      const label = row.favorability > 0 ? 'Благоприятная' : row.favorability < 0 ? 'Неблагоприятная' : 'Нейтральная';
      return <Chip label={`${label} (${row.favorability > 0 ? '+' : ''}${row.favorability})`} color={color} size="small" />;
    },
  },
  { key: 'name_ru', label: 'Название' },
  { key: 'description_ru', label: 'Описание', type: 'multiline', fullWidth: true },
];

const QIMEN_TRIGRAM_COLUMNS = [
  { key: 'trigram_id', label: 'ID', editable: false },
  { key: 'trigram_char', label: 'Символ', bold: true },
  { key: 'trigram_name_ru', label: 'Название (RU)' },
  { key: 'trigram_name_en', label: 'EN' },
  { key: 'trigram_name_zh', label: 'ZH' },
  { key: 'palace_nos', label: 'Дворцы', render: (row) => (Array.isArray(row.palace_nos) ? row.palace_nos.join(', ') : row.palace_nos) },
  { key: 'element', label: 'Элемент' },
  {
    key: 'nature',
    label: 'Характер',
    type: 'select',
    options: [
      { value: 'auspicious', label: 'Благоприятный' },
      { value: 'mixed', label: 'Смешанный' },
      { value: 'inauspicious', label: 'Неблагоприятный' },
    ],
    render: (row) => row.nature ? (
      <Chip label={CATEGORY_LABELS_RU[row.nature] || row.nature} color={CATEGORY_COLORS[row.nature] || 'default'} size="small" />
    ) : null,
  },
  { key: 'description_ru', label: 'Описание', type: 'multiline', fullWidth: true },
];

const SHENSHA_COLUMNS = [
  { key: 'config_id', label: 'ID', editable: false },
  { key: 'star_key', label: 'Ключ', editable: false },
  { key: 'display_name_ru', label: 'Название (RU)', bold: true },
  { key: 'display_name_zh', label: 'Название (ZH)' },
  {
    key: 'category',
    label: 'Категория',
    type: 'select',
    options: [
      { value: 'auspicious', label: 'Благоприятная' },
      { value: 'inauspicious', label: 'Неблагоприятная' },
      { value: 'relationships', label: 'Отношения' },
      { value: 'finance', label: 'Финансы' },
      { value: 'health', label: 'Здоровье' },
      { value: 'career', label: 'Карьера' },
      { value: 'intellect', label: 'Интеллект' },
      { value: 'travel', label: 'Путешествия' },
      { value: 'reputation', label: 'Репутация' },
      { value: 'general', label: 'Общая' },
      { value: 'neutral', label: 'Нейтральная' },
    ],
  },
  {
    key: 'nature',
    label: 'Характер',
    type: 'select',
    options: [
      { value: 'auspicious', label: 'Благоприятный' },
      { value: 'inauspicious', label: 'Неблагоприятный' },
      { value: 'mixed', label: 'Смешанный' },
      { value: 'neutral', label: 'Нейтральный' },
    ],
    render: (row) => row.nature ? (
      <Chip label={CATEGORY_LABELS_RU[row.nature] || row.nature} color={CATEGORY_COLORS[row.nature] || 'default'} size="small" />
    ) : null,
  },
  { key: 'color_hex', label: 'Цвет', type: 'color' },
  {
    key: 'is_active',
    label: 'Активна',
    type: 'select',
    options: [
      { value: 1, label: 'Да' },
      { value: 0, label: 'Нет' },
    ],
    render: (row) => (
      <Chip label={row.is_active ? 'Да' : 'Нет'} color={row.is_active ? 'success' : 'default'} size="small" />
    ),
  },
  { key: 'tooltip_text', label: 'Подсказка', type: 'multiline' },
  { key: 'short_interpretation', label: 'Краткая интерпретация' },
  { key: 'interpretation_text', label: 'Полная интерпретация', type: 'multiline', fullWidth: true },
  {
    key: 'source',
    label: 'Источник',
    type: 'select',
    options: [
      { value: 'classical', label: 'Классика' },
      { value: 'vladimir_zakharov', label: 'В. Захаров' },
    ],
    render: (row) => (
      <Chip
        label={row.source === 'vladimir_zakharov' ? 'В. Захаров' : 'Классика'}
        color={row.source === 'vladimir_zakharov' ? 'secondary' : 'primary'}
        size="small"
      />
    ),
  },
  { key: 'display_order', label: 'Порядок', type: 'number' },
];

function ReferencesPage() {
  const [tab, setTab] = useState(0);
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saveMessage, setSaveMessage] = useState(null);
  const [displayMode, setDisplayMode] = useState(() => {
    try {
      return localStorage.getItem('refs_display_mode') || 'text';
    } catch {
      return 'text';
    }
  });

  useEffect(() => {
    loadTabData(tab);
  }, [tab]);

  const loadTabData = async (tabIndex) => {
    setLoading(true);
    setError(null);
    try {
      const tabDef = TABS[tabIndex];
      const key = tabDef.key;
      if (data[key] && data[key].length > 0) {
        setLoading(false);
        return;
      }
      let tabData;
      if (key === 'officers') tabData = await refsService.fetchOfficers();
      else if (key === 'constellations') tabData = await refsService.fetchConstellations();
      else if (key === 'beltStars') tabData = await refsService.fetchBeltStars();
      else if (key === 'stems') tabData = await refsService.fetchHeavenlyStems();
      else if (key === 'branches') tabData = await refsService.fetchEarthlyBranches();
      else if (key === 'blackRabbit') tabData = await refsService.fetchBlackRabbitStars();
      else if (key === 'elements') tabData = await refsService.fetchElements();
      else if (key === 'shensha') tabData = await refsService.fetchShenShaConfig();
      else if (key === 'qimenStars') tabData = await qimenService.fetchStars();
      else if (key === 'qimenGates') tabData = await qimenService.fetchGates();
      else if (key === 'qimenSpirits') tabData = await qimenService.fetchSpirits();
      else if (key === 'qimenCombos') tabData = await qimenService.fetchStemCombos();
      else if (key === 'qimenTrigrams') tabData = await qimenService.fetchTrigrams();
      if (tabData) {
        setData(prev => ({ ...prev, [key]: tabData }));
      }
    } catch (err) {
      setError('Не удалось загрузить справочники. ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDisplayModeChange = (mode) => {
    setDisplayMode(mode);
    try {
      localStorage.setItem('refs_display_mode', mode);
    } catch {}
  };

  const handleSave = (serviceFn, dataKey, idField) => {
    return async (id, editData) => {
      try {
        await serviceFn(id, editData);
        setData(prev => ({
          ...prev,
          [dataKey]: prev[dataKey].map(o => (o[idField] === id ? editData : o)),
        }));
        setSaveMessage({ type: 'success', text: 'Сохранено' });
        setTimeout(() => setSaveMessage(null), 2000);
      } catch (err) {
        setSaveMessage({ type: 'error', text: 'Ошибка сохранения: ' + err.message });
        throw err;
      }
    };
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', maxWidth: '100%' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Справочники
      </Typography>
      {saveMessage && (
        <Alert severity={saveMessage.type} sx={{ mb: 2 }} onClose={() => setSaveMessage(null)}>
          {saveMessage.text}
        </Alert>
      )}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tab}
          onChange={(e, v) => { setTab(v); setSaveMessage(null); }}
          variant="scrollable"
          scrollButtons="auto"
        >
          {TABS.map((t, i) => (
            <Tab key={i} label={`${t.label} (${(data[t.key] || []).length})`} data-element-id={generateId('refs', 'tab', t.key)} />
          ))}
        </Tabs>
      </Paper>

      <Box sx={{ width: '100%', overflowX: 'auto' }}>
        {tab === 0 && (
          <SmartTable
            columns={OFFICER_COLUMNS}
            data={data.officers || []}
            idField="officer_value_id"
            onSaveRow={handleSave(refsService.updateOfficer, 'officers', 'officer_value_id')}
            storageKey="officers"
            categoryFilter={{
              key: 'officer_category',
              options: [
                { value: 'auspicious', label: 'Благоприятный' },
                { value: 'mixed', label: 'Смешанный' },
                { value: 'inauspicious', label: 'Неблагоприятный' },
              ],
            }}
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 1 && (
          <SmartTable
            columns={CONSTELLATION_COLUMNS}
            data={data.constellations || []}
            idField="constellation_id"
            onSaveRow={handleSave(refsService.updateConstellation, 'constellations', 'constellation_id')}
            storageKey="constellations"
            categoryFilter={{
              key: 'nature',
              options: [
                { value: 'auspicious', label: 'Благоприятный' },
                { value: 'mixed', label: 'Смешанный' },
                { value: 'inauspicious', label: 'Неблагоприятный' },
              ],
            }}
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 2 && (
          <SmartTable
            columns={BELT_COLUMNS}
            data={data.beltStars || []}
            idField="id"
            onSaveRow={handleSave(refsService.updateBeltStar, 'beltStars', 'id')}
            storageKey="beltStars"
            categoryFilter={{
              key: 'score',
              mapValue: (row) => row.score > 0 ? 'yellow' : row.score < 0 ? 'black' : 'neutral',
              options: [
                { value: 'yellow', label: 'Жёлтый' },
                { value: 'black', label: 'Чёрный' },
                { value: 'neutral', label: 'Нейтральный' },
              ],
            }}
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 3 && (
          <SmartTable
            columns={STEM_COLUMNS}
            data={data.stems || []}
            idField="stem_id"
            onSaveRow={handleSave(refsService.updateHeavenlyStem, 'stems', 'stem_id')}
            storageKey="stems"
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 4 && (
          <SmartTable
            columns={BRANCH_COLUMNS}
            data={data.branches || []}
            idField="branch_id"
            onSaveRow={handleSave(refsService.updateEarthlyBranch, 'branches', 'branch_id')}
            storageKey="branches"
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 5 && (
          <SmartTable
            columns={BLACK_RABBIT_COLUMNS}
            data={data.blackRabbit || []}
            idField="star_name"
            onSaveRow={handleSave(refsService.updateBlackRabbitStar, 'blackRabbit', 'star_name')}
            storageKey="blackRabbit"
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 6 && (
          <SmartTable
            columns={ELEMENT_COLUMNS}
            data={data.elements || []}
            idField="element_id"
            onSaveRow={handleSave(refsService.updateElement, 'elements', 'element_id')}
            storageKey="elements"
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 7 && (
          <SmartTable
            columns={SHENSHA_COLUMNS}
            data={data.shensha || []}
            idField="config_id"
            onSaveRow={handleSave(refsService.updateShenShaConfig, 'shensha', 'config_id')}
            storageKey="shensha"
            categoryFilter={{
              key: 'nature',
              options: [
                { value: 'auspicious', label: 'Благоприятный' },
                { value: 'mixed', label: 'Смешанный' },
                { value: 'inauspicious', label: 'Неблагоприятный' },
                { value: 'neutral', label: 'Нейтральный' },
              ],
            }}
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 8 && (
          <SmartTable
            columns={QIMEN_STAR_COLUMNS}
            data={data.qimenStars || []}
            idField="star_id"
            storageKey="qimenStars"
            categoryFilter={{
              key: 'nature',
              options: [
                { value: 'auspicious', label: 'Благоприятный' },
                { value: 'mixed', label: 'Смешанный' },
                { value: 'inauspicious', label: 'Неблагоприятный' },
              ],
            }}
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 9 && (
          <SmartTable
            columns={QIMEN_GATE_COLUMNS}
            data={data.qimenGates || []}
            idField="gate_id"
            storageKey="qimenGates"
            categoryFilter={{
              key: 'nature',
              options: [
                { value: 'auspicious', label: 'Благоприятный' },
                { value: 'mixed', label: 'Смешанный' },
                { value: 'inauspicious', label: 'Неблагоприятный' },
              ],
            }}
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 10 && (
          <SmartTable
            columns={QIMEN_SPIRIT_COLUMNS}
            data={data.qimenSpirits || []}
            idField="spirit_id"
            storageKey="qimenSpirits"
            categoryFilter={{
              key: 'nature',
              options: [
                { value: 'auspicious', label: 'Благоприятный' },
                { value: 'mixed', label: 'Смешанный' },
                { value: 'inauspicious', label: 'Неблагоприятный' },
              ],
            }}
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 11 && (
          <SmartTable
            columns={QIMEN_COMBO_COLUMNS}
            data={data.qimenCombos || []}
            idField="combo_id"
            storageKey="qimenCombos"
            categoryFilter={{
              key: 'favorability',
              mapValue: (row) => row.favorability > 0 ? 'positive' : row.favorability < 0 ? 'negative' : 'neutral',
              options: [
                { value: 'positive', label: 'Благоприятная' },
                { value: 'negative', label: 'Неблагоприятная' },
                { value: 'neutral', label: 'Нейтральная' },
              ],
            }}
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
        {tab === 12 && (
          <SmartTable
            columns={QIMEN_TRIGRAM_COLUMNS}
            data={data.qimenTrigrams || []}
            idField="trigram_id"
            storageKey="qimenTrigrams"
            displayMode={displayMode}
            onDisplayModeChange={handleDisplayModeChange}
          />
        )}
      </Box>
    </Box>
  );
}

export default ReferencesPage;
