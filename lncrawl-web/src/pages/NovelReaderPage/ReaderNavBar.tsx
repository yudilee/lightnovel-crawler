import cx from 'classnames';
import styles from './ReaderNavBar.module.scss';

import { store } from '@/store';
import { Reader } from '@/store/_reader';
import type { ReadChapter } from '@/types';
import {
  BorderOutlined,
  LeftOutlined,
  RightOutlined,
  SoundOutlined,
  StepBackwardOutlined,
  StepForwardOutlined,
} from '@ant-design/icons';
import { Flex, Grid } from 'antd';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { ReaderSettingsButton } from './ReaderSettingsButton';

export const ReaderNavBar: React.FC<{
  data: ReadChapter;
}> = ({ data }) => {
  const { md } = Grid.useBreakpoint();
  const theme = useSelector(Reader.select.theme);
  const speaking = useSelector(Reader.select.speaking);

  return (
    <Flex
      align="center"
      justify="center"
      style={{
        color: theme.color,
        background: md ? theme.background : theme.background + 'e5',
      }}
      className={cx(styles.readerNavBar, { [styles.mobile]: !md })}
    >
      {speaking ? <SpeechNavs data={data} /> : <GeneralNavs data={data} />}
    </Flex>
  );
};

const GeneralNavs: React.FC<{
  data: ReadChapter;
}> = ({ data }) => {
  const navigate = useNavigate();
  const { sm } = Grid.useBreakpoint();

  const startSpeaking = () => {
    window.speechSynthesis.cancel();
    store.dispatch(Reader.action.setSpeaking(true));
  };

  const goPrevious = () => {
    if (data.previous_id) {
      navigate(`/read/${data.previous_id}`);
    }
  };

  const goNext = () => {
    if (data.next_id) {
      navigate(`/read/${data.next_id}`);
    }
  };

  return (
    <>
      <div
        onClick={goPrevious}
        className={cx(styles.item, {
          [styles.disabled]: !data.previous_id,
        })}
      >
        <LeftOutlined />
        {sm && ' Previous'}
      </div>

      <div className={styles.item} onClick={startSpeaking}>
        <SoundOutlined />
        {sm && 'Read'}
      </div>

      <ReaderSettingsButton className={styles.item} />

      <div
        onClick={goNext}
        className={cx(styles.item, {
          [styles.disabled]: !data.next_id,
        })}
      >
        {sm && 'Next '}
        <RightOutlined />
      </div>
    </>
  );
};

const SpeechNavs: React.FC<{
  data: ReadChapter;
}> = () => {
  const { sm } = Grid.useBreakpoint();
  const position = useSelector(Reader.select.speakPosition);

  const stopSpeaking = () => {
    store.dispatch(Reader.action.setSpeaking(false));
    window.speechSynthesis.cancel();
  };

  const moveBackward = () => {
    store.dispatch(Reader.action.setSepakPosition(position - 1));
  };

  const moveForward = () => {
    store.dispatch(Reader.action.setSepakPosition(position + 1));
  };

  return (
    <>
      <div
        onClick={moveBackward}
        className={cx(styles.item, {
          [styles.disabled]: position === 0,
        })}
      >
        <StepBackwardOutlined />
        {sm && 'Backward'}
      </div>
      <div className={styles.item} onClick={stopSpeaking}>
        <BorderOutlined />
        {sm && 'Stop'}
      </div>
      <div className={styles.item} onClick={moveForward}>
        <StepForwardOutlined />
        {sm && 'Forward'}
      </div>
    </>
  );
};
