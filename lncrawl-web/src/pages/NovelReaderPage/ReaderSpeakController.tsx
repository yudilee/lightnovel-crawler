import cx from 'classnames';
import styles from './ReaderNavBar.module.scss';

import { store } from '@/store';
import { Reader } from '@/store/_reader';
import {
  BorderOutlined,
  StepBackwardOutlined,
  StepForwardOutlined,
} from '@ant-design/icons';
import { Grid } from 'antd';
import { useSelector } from 'react-redux';

export const ReaderSpeakController: React.FC<
  React.HTMLAttributes<HTMLDivElement>
> = (props) => {
  const { sm } = Grid.useBreakpoint();
  const position = useSelector(Reader.select.speakPosition);

  const toggleSpeaking = () => {
    store.dispatch(Reader.action.setSpeaking(false));
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
        {...props}
        onClick={moveBackward}
        className={cx(props.className, {
          [styles.disabled]: position === 0,
        })}
      >
        <StepBackwardOutlined />
        {sm && 'Backward'}
      </div>
      <div {...props} onClick={toggleSpeaking}>
        <BorderOutlined />
        {sm && 'Stop'}
      </div>
      <div {...props} onClick={moveForward}>
        <StepForwardOutlined />
        {sm && 'Forward'}
      </div>
    </>
  );
};
