import { store } from '@/store';
import { Reader } from '@/store/_reader';
import { SoundOutlined } from '@ant-design/icons';
import { Select } from 'antd';
import { useSelector } from 'react-redux';
import type { ReaderSettingsItem } from '.';

export const ReaderVoiceSettings: ReaderSettingsItem = {
  label: 'Voice',
  icon: <SoundOutlined />,
  component: () => {
    const voice = useSelector(Reader.select.voice);

    const updateVoice = (value: string) => {
      store.dispatch(Reader.action.setVoice(value));
    };

    const voices = window.speechSynthesis.getVoices();
    const defaultValue = voices.find((x) => x.default)?.voiceURI;

    const options = voices.map((voice) => ({
      value: voice.voiceURI,
      label: voice.name,
    }));

    return (
      <Select
        variant="borderless"
        style={{ width: '100%' }}
        placeholder="Select a voice"
        defaultValue={defaultValue}
        value={voice}
        onSelect={updateVoice}
        options={options}
      />
    );
  },
};
