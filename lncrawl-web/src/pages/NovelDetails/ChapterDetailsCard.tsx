import { type Chapter } from '@/types';
import { formatDate } from '@/utils/time';
import { RightCircleOutlined } from '@ant-design/icons';
import { Button, Card, Descriptions, Grid } from 'antd';
import { useNavigate } from 'react-router-dom';

export const ChapterDetailsCard: React.FC<{
  chapter: Chapter;
  inner?: boolean;
}> = ({ chapter, inner }) => {
  const navigate = useNavigate();
  const { lg } = Grid.useBreakpoint();

  return (
    <Card
      type={inner ? 'inner' : undefined}
      title={inner ? undefined : chapter.title}
      variant={inner ? 'borderless' : 'outlined'}
      styles={{
        body: {
          padding: 10,
        },
        title: {
          fontSize: 22,
          whiteSpace: 'wrap',
        },
      }}
      extra={
        !inner && chapter.is_available ? (
          <Button
            shape="round"
            icon={<RightCircleOutlined />}
            onClick={() => navigate(`/read/${chapter.id}`)}
          >
            Read
          </Button>
        ) : undefined
      }
    >
      <Descriptions
        size="small"
        layout="horizontal"
        column={lg ? 3 : 1}
        bordered
        items={[
          {
            label: 'URL',
            span: 3,
            children: (
              <a href={chapter.url} target="_blank">
                {chapter.url}
              </a>
            ),
          },
          {
            label: 'Serial',
            children: chapter.serial,
          },
          {
            label: 'Available',
            children: chapter.is_available ? 'Yes' : 'No',
          },
          {
            label: 'Last Update',
            children: formatDate(chapter.updated_at),
          },
        ]}
      />
    </Card>
  );
};
