import { store } from '@/store';
import { Reader } from '@/store/_reader';
import { FontFamily } from '@/types';
import { FontColorsOutlined } from '@ant-design/icons';
import { Select } from 'antd';
import { startCase } from 'lodash';
import { useSelector } from 'react-redux';
import type { ReaderSettingsItem } from './types';

export const ReaderFontFamilySettings: ReaderSettingsItem = {
  label: 'Font Family',
  icon: <FontColorsOutlined />,
  component: () => {
    const fontFamily = useSelector(Reader.select.fontFamily);

    const updateFontFamily = (value: FontFamily) => {
      store.dispatch(Reader.action.setFontFamily(value));
    };

    const options = Object.entries(FontFamily).map(([name, value]) => ({
      value,
      label: <span style={{ fontFamily: value }}>{startCase(name)}</span>,
    }));

    return (
      <Select
        virtual={false}
        placeholder="Select font family"
        variant="borderless"
        style={{ width: '100%' }}
        options={options}
        value={fontFamily}
        onSelect={updateFontFamily}
      />
    );
  },
};
