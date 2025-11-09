import { type Artifact } from '@/types';
import { Card, Empty, List } from 'antd';
import { ArtifactListItemCard } from './ArtifactListItemCard';

export const ArtifactListCard: React.FC<{ artifacts?: Artifact[] }> = ({
  artifacts,
}) => {
  return (
    <Card
      title="Artifacts"
      variant="outlined"
      styles={{ body: { paddingTop: 5, paddingBottom: 5 } }}
    >
      {artifacts && artifacts.length > 0 ? (
        <List
          dataSource={artifacts}
          renderItem={(item) => <ArtifactListItemCard artifact={item} />}
        />
      ) : (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="No artifacts"
        />
      )}
    </Card>
  );
};
