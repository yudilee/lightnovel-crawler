import { AudioMutedOutlined, SoundOutlined } from '@ant-design/icons';
import { Button, Grid } from 'antd';
import { useEffect, useState } from 'react';

export const ReaderTextToSpeechButton: React.FC<any> = () => {
  const { sm } = Grid.useBreakpoint();
  const [speaking, setSpeaking] = useState(false);

  if (!window.speechSynthesis) {
    return null;
  }

  const startSpeaking = () => {
    const ut = new SpeechSynthesisUtterance('Hello There');
    window.speechSynthesis.getVoices();
    window.speechSynthesis.speak(ut);
  };

  return (
    <>
      <Button
        size="large"
        style={{ borderRadius: 0 }}
        onClick={startSpeaking} //() => setSpeaking((v) => !v)}
        icon={speaking ? <AudioMutedOutlined /> : <SoundOutlined />}
      >
        {sm && 'Read'}
      </Button>
    </>
  );
};
