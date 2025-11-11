import { type Chapter } from '@/types';
import { formatDate } from '@/utils/time';
import { Card, Descriptions, Grid } from 'antd';

export const ChapterDetailsCard: React.FC<{
  chapter: Chapter;
}> = ({ chapter }) => {
  const { lg } = Grid.useBreakpoint();
  return (
    <Card
      size="small"
      variant="outlined"
      title={chapter.title}
      styles={{
        title: {
          fontSize: 22,
          padding: 10,
          whiteSpace: 'wrap',
        },
      }}
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
            label: 'Created',
            children: formatDate(chapter.created_at),
          },
        ]}
      />
    </Card>
  );
};
