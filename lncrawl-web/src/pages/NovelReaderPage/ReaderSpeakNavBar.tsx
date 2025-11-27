import cx from 'classnames';
import styles from './ReaderNavBar.module.scss';

import { store } from '@/store';
import { Reader } from '@/store/_reader';
import type { ReadChapter } from '@/types';
import {
  BorderOutlined,
  StepBackwardOutlined,
  StepForwardOutlined,
} from '@ant-design/icons';
import { Flex, Grid } from 'antd';
import { useSelector } from 'react-redux';
import { focusReaderPosition } from './utils';
import { useNavigate } from 'react-router-dom';

export const ReaderSpeakNavVar: React.FC<{
  data: ReadChapter;
}> = ({ data }) => {
  const navigate = useNavigate();
  const { sm, md } = Grid.useBreakpoint();
  const theme = useSelector(Reader.select.theme);
  const position = useSelector(Reader.select.speakPosition);

  const stopSpeaking = () => {
    store.dispatch(Reader.action.setSpeaking(false));
    window.speechSynthesis.cancel();
  };

  const moveBackward = () => {
    if (position === 0) {
      if (data.previous_id) {
        navigate(`/read/${data.previous_id}`);
      }
    } else {
      store.dispatch(Reader.action.setSepakPosition(position - 1));
      focusReaderPosition(position - 1);
    }
  };

  const moveForward = () => {
    store.dispatch(Reader.action.setSepakPosition(position + 1));
    focusReaderPosition(position + 1);
  };

  return (
    <Flex
      align="center"
      justify="center"
      className={cx(styles.readerNavBar, {
        [styles.mobile]: !md,
      })}
      style={{
        bottom: 0,
        color: theme.color,
        background: md ? theme.background : theme.background + 'e5',
      }}
    >
      <div onClick={moveBackward} className={styles.item}>
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
    </Flex>
  );
};
