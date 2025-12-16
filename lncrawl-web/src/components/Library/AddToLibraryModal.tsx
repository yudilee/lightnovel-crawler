import { Modal } from 'antd';
import { useState } from 'react';
import { CreateLibraryView } from './CreateLibraryView';
import { LibrarySelectionView } from './LibrarySelectionView';
import type { Library } from '@/types';

type View = 'selection' | 'create';

interface Props {
  novelId: string;
  open: boolean;
  onCancel: () => void;
}

export const AddToLibraryModal: React.FC<Props> = ({
  novelId,
  open,
  onCancel,
}) => {
  const [view, setView] = useState<View>('selection');
  const [library, setLibrary] = useState<Library | undefined>();

  const handleCancel = () => {
    setView('selection');
    onCancel();
  };

  const handleCreateSuccess = async (library: Library) => {
    setLibrary(library);
    setView('selection');
  };

  const handleSelectionSuccess = () => {
    handleCancel();
  };

  return (
    <Modal
      title="Add to Library"
      open={open}
      onCancel={handleCancel}
      footer={null}
      destroyOnHidden
    >
      {view === 'selection' ? (
        <LibrarySelectionView
          library={library}
          novelId={novelId}
          onCreateNew={() => setView('create')}
          onSuccess={handleSelectionSuccess}
        />
      ) : (
        <CreateLibraryView
          novelId={novelId}
          onBack={() => setView('selection')}
          onSuccess={handleCreateSuccess}
        />
      )}
    </Modal>
  );
};
