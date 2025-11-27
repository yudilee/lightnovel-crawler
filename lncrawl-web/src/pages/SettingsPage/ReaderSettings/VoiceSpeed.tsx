import { store } from '@/store';
import { Reader } from '@/store/_reader';
import { FastForwardOutlined } from '@ant-design/icons';
import { Flex, Slider, Tag } from 'antd';
import { useSelector } from 'react-redux';
import type { ReaderSettingsItem } from './types';

export const ReaderVoiceSpeedSettings: ReaderSettingsItem = {
  label: 'Speed',
  icon: <FastForwardOutlined />,
  component: () => {
    const voiceSpeed = useSelector(Reader.select.voiceSpeed);

    const updateVoiceSpeed = (value: number) => {
      store.dispatch(Reader.action.setVoiceSpeed(value));
    };

    return (
      <Flex align="center">
        <Tag style={{ fontSize: 12, userSelect: 'none' }}>{voiceSpeed}</Tag>
        <Slider
          min={0.1}
          max={2}
          step={0.1}
          value={voiceSpeed}
          onChange={updateVoiceSpeed}
          style={{ flex: 1 }}
        />
      </Flex>
    );
  },
};
