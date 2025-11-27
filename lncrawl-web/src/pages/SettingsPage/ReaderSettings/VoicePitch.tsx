import { store } from '@/store';
import { Reader } from '@/store/_reader';
import { RiseOutlined } from '@ant-design/icons';
import { Flex, Slider, Tag } from 'antd';
import { useSelector } from 'react-redux';
import type { ReaderSettingsItem } from './types';

export const ReaderVoicePitchSettings: ReaderSettingsItem = {
  label: 'Pitch',
  icon: <RiseOutlined />,
  component: () => {
    const voicePitch = useSelector(Reader.select.voicePitch);

    const updateVoicePitch = (value: number) => {
      store.dispatch(Reader.action.setVoicePitch(value));
    };

    return (
      <Flex align="center">
        <Tag style={{ fontSize: 12, userSelect: 'none' }}>{voicePitch}</Tag>
        <Slider
          min={0.1}
          max={2}
          step={0.1}
          value={voicePitch}
          onChange={updateVoicePitch}
          style={{ flex: 1 }}
        />
      </Flex>
    );
  },
};
