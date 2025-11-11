import { type Volume } from '@/types';
import { formatDate } from '@/utils/time';
import { Card, Descriptions, Grid } from 'antd';

export const VolumeDetailsCard: React.FC<{
  volume: Volume;
}> = ({ volume }) => {
  const { lg } = Grid.useBreakpoint();
  return (
    <Card
      size="small"
      variant="outlined"
      title={volume.title}
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
            label: 'Serial',
            children: volume.serial,
          },
          {
            label: 'Chapters',
            children: volume.chapter_count ?? 0,
          },
          {
            label: 'Created',
            children: formatDate(volume.created_at),
          },
        ]}
      />
    </Card>
  );
};
