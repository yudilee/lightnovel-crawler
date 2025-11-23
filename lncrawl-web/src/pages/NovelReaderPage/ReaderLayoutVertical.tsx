import cx from 'classnames';
import styles from './ReaderLayoutVertical.module.scss';

import { Reader } from '@/store/_reader';
import type { ReadChapter } from '@/types';
import { Divider, Empty, Flex, Grid, Typography } from 'antd';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { ReaderVerticalContent } from './ReaderLayoutVerticalContent';
import { ReaderNavBar } from './ReaderNavBar';

export const ReaderVerticalLayout: React.FC<{
  data: ReadChapter;
}> = ({ data }) => {
  const { md } = Grid.useBreakpoint();
  const theme = useSelector(Reader.select.theme);
  const fontSize = useSelector(Reader.select.fontSize);
  const lineHeight = useSelector(Reader.select.lineHeight);
  const fontFamily = useSelector(Reader.select.fontFamily);

  return (
    <Flex
      vertical
      style={{ fontSize, lineHeight, fontFamily, ...theme }}
      className={cx('novel-reader', styles.layout, { [styles.mobile]: !md })}
    >
      <div style={{ textAlign: 'center' }}>
        <Typography.Title level={4} style={{ margin: 0, color: '#F16C6F' }}>
          {data.novel.authors}
        </Typography.Title>
        <Typography.Title level={1} style={{ margin: 0 }}>
          <Link to={`/novel/${data.novel.id}`} style={{ color: '#8484F4' }}>
            {data.novel.title}
          </Link>
        </Typography.Title>
      </div>

      <Divider size="middle" style={{ background: theme.color + '44' }} />
      <ReaderNavBar data={data} />

      {data.content ? (
        <ReaderVerticalContent data={data} />
      ) : (
        <Empty
          description="No contents available"
          styles={{ description: { color: theme.color } }}
          style={{ padding: `calc(50vh - ${md ? 164 : 176}px) 0` }}
        />
      )}
    </Flex>
  );
};
