import { store } from '@/store';
import { Reader } from '@/store/_reader';
import { SoundOutlined } from '@ant-design/icons';
import { Select } from 'antd';
import { useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import type { ReaderSettingsItem } from './types';

export function getVoices(): Promise<SpeechSynthesisVoice[]> {
  return new Promise((resolve) => {
    if (!window.speechSynthesis) {
      return resolve([]);
    }
    let interval: any, timeout: any;
    interval = setInterval(() => {
      const voices = speechSynthesis.getVoices();
      if (voices.length) {
        clearTimeout(timeout);
        clearInterval(interval);
        resolve(voices);
      }
    }, 50);
    timeout = setTimeout(() => {
      clearInterval(interval);
      clearTimeout(timeout);
      clearInterval(interval);
      resolve([]);
    }, 10000);
  });
}

export const ReaderVoiceSettings: ReaderSettingsItem = {
  label: 'Voice',
  icon: <SoundOutlined />,
  component: () => {
    const voice = useSelector(Reader.select.voice);

    const [loading, setLoading] = useState<boolean>(true);
    const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);

    useEffect(() => {
      getVoices()
        .then(setVoices)
        .finally(() => setLoading(false));
    }, []);

    const defaultValue = useMemo(
      () => voices.find((x) => x.default)?.voiceURI,
      [voices]
    );

    const options = useMemo(
      () =>
        voices.map((voice) => ({
          label: voice.name,
          value: voice.voiceURI,
        })),
      [voices]
    );

    const updateVoice = (value: string) => {
      store.dispatch(Reader.action.setVoice(value));
    };

    return (
      <Select
        loading={loading}
        disabled={!voices.length}
        variant="borderless"
        style={{ width: '100%' }}
        placeholder="Select a voice"
        defaultValue={defaultValue}
        value={voice}
        options={options}
        onSelect={updateVoice}
        title={
          !voices.length
            ? 'Speech Synthesis is not available for this browser'
            : undefined
        }
      />
    );
  },
};
