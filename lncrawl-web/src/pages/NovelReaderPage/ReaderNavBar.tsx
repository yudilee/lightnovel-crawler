import type { ReadChapter } from '@/types';
import { LeftOutlined, RightOutlined } from '@ant-design/icons';
import { Button, Flex, Grid } from 'antd';
import { useNavigate } from 'react-router-dom';
import { ReaderContentsButton } from './ReaderContentsButton';
import { ReaderSettingsButton } from './ReaderSettingsButton';

export const ReaderNavBar: React.FC<{
  data: ReadChapter;
}> = ({ data }) => {
  const navigate = useNavigate();
  const { sm } = Grid.useBreakpoint();
  return (
    <Flex
      align="center"
      justify="center"
      style={{
        margin: 7,
        boxShadow: `5px solid #000`,
      }}
    >
      <Button
        size="large"
        shape="round"
        disabled={!data.previous_id}
        onClick={() => navigate(`/read/${data.previous_id}`)}
        style={{
          borderTopRightRadius: 0,
          borderBottomRightRadius: 0,
        }}
      >
        <LeftOutlined />
        {sm && ' Previous'}
      </Button>

      <ReaderContentsButton novelId={data.novel.id} />
      <ReaderSettingsButton />

      <Button
        size="large"
        shape="round"
        disabled={!data.next_id}
        onClick={() => navigate(`/read/${data.next_id}`)}
        style={{
          borderTopLeftRadius: 0,
          borderBottomLeftRadius: 0,
        }}
      >
        {sm && 'Next '}
        <RightOutlined />
      </Button>
    </Flex>
  );
};
