import { store } from '@/store';
import { Reader } from '@/store/_reader';
import { LineHeightOutlined } from '@ant-design/icons';
import { Slider } from 'antd';
import { useSelector } from 'react-redux';
import type { ReaderSettingsItem } from '.';

export const ReaderLineHeightSettings: ReaderSettingsItem = {
  label: 'Line Height',
  icon: <LineHeightOutlined />,
  component: () => {
    const lineHeight = useSelector(Reader.select.lineHeight);

    const updateLineHeight = (value: number) => {
      store.dispatch(Reader.action.setLineHeight(value));
    };

    return (
      <Slider
        min={0.5}
        max={2.5}
        step={0.05}
        value={lineHeight}
        onChange={updateLineHeight}
      />
    );
  },
};
